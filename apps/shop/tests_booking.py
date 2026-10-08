"""Phase 2: 1-on-1 bookings against the school calendar.

A slot is offered only inside the educator's weekly hours, clear of their platform
sessions, their time off and other bookings (each widened by the buffer). Holding
it puts the session in the cart; paying confirms it and creates the live session.
Students may reschedule but not cancel; staff/educator cancellations become credit.
"""
from datetime import time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.communication.models import MeetingRoom, Notification
from apps.finance import models as finance
from apps.finance import services as finance_services

from . import booking, checkout
from .models import (Booking, CreditEntry, EducatorAvailability, EducatorRate, EducatorTimeOff,
                     Order, Product)
from .tests import _onboarded

User = get_user_model()


@override_settings(MS_TEAMS_ENABLED=False, VAT_REGISTERED=False, PAYMENTS_ENABLED=True)
class BookingTests(TestCase):
    def setUp(self):
        self.student = _onboarded(User.objects.create_user('stu', 'stu@example.com', 'pw12345!',
                                                           first_name='Thandi'))
        self.other = _onboarded(User.objects.create_user('oth', 'oth@example.com', 'pw12345!'))
        teacher = User.objects.create_user('edu', 'edu@example.com', 'pw12345!', first_name='Tumi')
        self.educator = teacher.profile
        self.educator.user_type = 'educator'
        self.educator.first_name, self.educator.last_name = 'Tumi', 'Mokoena'
        self.educator.registered = self.educator.profile_status = True
        self.educator.save()
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pw12345!', is_staff=True)

        self.service = Product.objects.create(name='Tax consult', fulfilment=Product.FULFIL_BOOKING,
                                              price=Decimal('400'))
        self.rate = EducatorRate.objects.create(product=self.service, educator=self.educator,
                                                hourly_rate=Decimal('450'))
        self.day = timezone.localdate() + timedelta(days=3)
        EducatorAvailability.objects.create(educator=self.educator, weekday=self.day.weekday(),
                                            start_time=time(9), end_time=time(12))

    def at(self, hour, minute=0):
        return timezone.make_aware(timezone.datetime.combine(self.day, time(hour, minute)),
                                   timezone.get_current_timezone())

    def slots(self, minutes=60):
        return [timezone.localtime(s).strftime('%H:%M')
                for s in booking.free_slots(self.rate, self.day, minutes)]

    # ---- availability ------------------------------------------------------
    def test_slots_follow_working_hours(self):
        self.assertEqual(self.slots(60), ['09:00', '09:30', '10:00', '10:30', '11:00'])
        self.assertEqual(self.slots(120), ['09:00', '09:30', '10:00'])
        self.assertEqual(booking.free_slots(self.rate, self.day + timedelta(days=1), 60), [])

    def test_hosted_session_and_buffer_block_time(self):
        MeetingRoom.objects.create(title='Class', host=self.educator.user,
                                   scheduled_start=self.at(10), scheduled_end=self.at(10, 30))
        # 10:00–10:30 busy, widened by 15 min: nothing may touch 09:45–10:45.
        self.assertEqual(self.slots(30), ['09:00', '11:00', '11:30'])

    def test_time_off_and_notice_block_time(self):
        EducatorTimeOff.objects.create(educator=self.educator, start=self.at(9), end=self.at(11))
        self.assertEqual(self.slots(60), ['11:00'])
        self.service.min_notice_hours = 24 * 5
        self.service.save()
        self.rate.refresh_from_db()
        self.assertEqual(self.slots(60), [])

    # ---- hold → pay → confirm ---------------------------------------------
    def test_hold_puts_priced_session_in_cart_and_blocks_the_slot(self):
        held = booking.hold_slot(user=self.student, rate=self.rate, start=self.at(9), minutes=90)
        item = Order.get_cart(self.student).items.get()
        self.assertEqual(item.unit_price, Decimal('675.00'))  # 450/h × 1.5h
        self.assertEqual(item.booking, held)
        with self.assertRaises(booking.BookingError):
            booking.hold_slot(user=self.other, rate=self.rate, start=self.at(10), minutes=60)
        self.assertNotIn('09:00', self.slots(30))

    def test_removing_from_cart_frees_the_slot(self):
        booking.hold_slot(user=self.student, rate=self.rate, start=self.at(9), minutes=60)
        Order.get_cart(self.student).items.get().delete()
        self.assertIn('09:00', self.slots(60))

    def test_payment_confirms_and_creates_the_session(self):
        held = booking.hold_slot(user=self.student, rate=self.rate, start=self.at(9), minutes=60)
        invoice = checkout.place_order(Order.get_cart(self.student), user=self.student)
        self.assertEqual(invoice.total, Decimal('450.00'))
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-B1')
        held.refresh_from_db()
        self.assertEqual(held.status, Booking.STATUS_CONFIRMED)
        self.assertIsNotNone(held.meeting)
        self.assertEqual(held.meeting.scheduled_start, self.at(9))
        self.assertTrue(held.meeting.participants.filter(user=self.student).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.student, verb='booking confirmed').exists())
        self.assertTrue(Notification.objects.filter(recipient=self.educator.user, verb='booking').exists())
        # The confirmed session (and its platform meeting) now occupy the time.
        self.assertNotIn('09:00', self.slots(60))

    def test_late_payment_for_a_lost_slot_becomes_credit(self):
        held = booking.hold_slot(user=self.student, rate=self.rate, start=self.at(9), minutes=60)
        invoice = checkout.place_order(Order.get_cart(self.student), user=self.student)
        Booking.objects.filter(pk=held.pk).update(status=Booking.STATUS_EXPIRED)
        rival = booking.hold_slot(user=self.other, rate=self.rate, start=self.at(9), minutes=60)
        Booking.objects.filter(pk=rival.pk).update(status=Booking.STATUS_CONFIRMED)

        finance_services.settle_payment(invoice, invoice.balance, gateway_ref='PF-B2')
        held.refresh_from_db()
        self.assertEqual(held.status, Booking.STATUS_CANCELLED)
        self.assertEqual(CreditEntry.balance_for(self.student), Decimal('450.00'))

    # ---- reschedule / cancel / credit -------------------------------------
    def _confirmed(self, hour=9):
        held = booking.hold_slot(user=self.student, rate=self.rate, start=self.at(hour), minutes=60)
        invoice = checkout.place_order(Order.get_cart(self.student), user=self.student)
        finance_services.settle_payment(invoice, invoice.balance, gateway_ref=f'PF-{hour}')
        held.refresh_from_db()
        return held

    def test_student_can_reschedule_before_cutoff(self):
        confirmed = self._confirmed()
        booking.reschedule(confirmed, start=self.at(11), by=self.student)
        confirmed.refresh_from_db()
        self.assertEqual(confirmed.start, self.at(11))
        self.assertEqual(confirmed.meeting.scheduled_start, self.at(11))
        self.assertIn('09:00', self.slots(60))

    def test_student_cannot_reschedule_inside_cutoff(self):
        confirmed = self._confirmed()
        self.service.reschedule_cutoff_hours = 24 * 10
        self.service.save()
        confirmed.refresh_from_db()
        with self.assertRaises(booking.BookingError):
            booking.reschedule(confirmed, start=self.at(11), by=self.student)

    def test_students_cannot_cancel(self):
        confirmed = self._confirmed()
        with self.assertRaises(booking.BookingError):
            booking.cancel(confirmed, by=self.student)
        self.client.force_login(self.student)
        self.client.post(reverse('shop:cancel-booking', args=[confirmed.pk]))
        confirmed.refresh_from_db()
        self.assertEqual(confirmed.status, Booking.STATUS_CONFIRMED)

    def test_educator_cancel_credits_the_student_and_credit_pays_next_order(self):
        confirmed = self._confirmed()
        booking.cancel(confirmed, by=self.educator.user, reason='Ill')
        confirmed.refresh_from_db()
        self.assertEqual(confirmed.status, Booking.STATUS_CANCELLED)
        self.assertFalse(confirmed.meeting.is_active)
        self.assertEqual(CreditEntry.balance_for(self.student), Decimal('450.00'))

        booking.hold_slot(user=self.student, rate=self.rate, start=self.at(11), minutes=60)
        invoice = checkout.place_order(Order.get_cart(self.student), user=self.student, use_credit=True)
        self.assertEqual(invoice.status, finance.Invoice.STATUS_PAID)
        self.assertEqual(CreditEntry.balance_for(self.student), Decimal('0'))

    def test_expired_unpaid_hold_is_released(self):
        held = booking.hold_slot(user=self.student, rate=self.rate, start=self.at(9), minutes=60)
        checkout.place_order(Order.get_cart(self.student), user=self.student)
        Booking.objects.filter(pk=held.pk).update(hold_expires_at=timezone.now() - timedelta(minutes=1))
        booking.run_housekeeping()
        held.refresh_from_db()
        self.assertEqual(held.status, Booking.STATUS_EXPIRED)
        self.assertIn('09:00', self.slots(60))

    # ---- views ------------------------------------------------------------
    def test_picker_page_and_hold_view(self):
        self.client.force_login(self.student)
        url = reverse('shop:product-detail', args=[self.service.pk])
        page = self.client.get(url, {'educator': self.rate.pk, 'minutes': 60,
                                     'day': self.day.isoformat()})
        self.assertContains(page, '09:00')
        self.assertContains(page, 'Checked against the school calendar')
        response = self.client.post(url, {'action': 'book', 'rate': self.rate.pk, 'minutes': 60,
                                          'start': self.at(10).isoformat()})
        self.assertRedirects(response, reverse('shop:cart'), fetch_redirect_response=False)
        self.assertEqual(Booking.objects.get().start, self.at(10))
        self.assertContains(self.client.get(reverse('shop:cart')), 'Tumi')

    def test_bookings_pages_render(self):
        self._confirmed()
        self.client.force_login(self.student)
        self.assertContains(self.client.get(reverse('shop:my-bookings')), 'Tax consult')
        self.client.force_login(self.educator.user)
        self.assertContains(self.client.get(reverse('shop:my-bookings')), 'Thandi')
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('shop:educators')).status_code, 200)
        self.assertEqual(self.client.get(reverse('shop:educator-hours', args=[self.educator.pk])).status_code, 200)

    def test_staff_sets_hours(self):
        self.client.force_login(self.staff)
        url = reverse('shop:educator-hours', args=[self.educator.pk])
        existing = EducatorAvailability.objects.get()
        self.client.post(url, {
            'hours-TOTAL_FORMS': '2', 'hours-INITIAL_FORMS': '1', 'hours-MIN_NUM_FORMS': '0', 'hours-MAX_NUM_FORMS': '1000',
            'hours-0-id': existing.pk, 'hours-0-educator': self.educator.pk, 'hours-0-weekday': existing.weekday,
            'hours-0-start_time': '09:00', 'hours-0-end_time': '12:00',
            'hours-1-educator': self.educator.pk, 'hours-1-weekday': '0', 'hours-1-start_time': '14:00', 'hours-1-end_time': '18:00',
            'away-TOTAL_FORMS': '0', 'away-INITIAL_FORMS': '0', 'away-MIN_NUM_FORMS': '0', 'away-MAX_NUM_FORMS': '1000',
        })
        self.assertEqual(EducatorAvailability.objects.filter(educator=self.educator).count(), 2)
