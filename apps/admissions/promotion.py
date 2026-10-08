"""Year-end promotion and the next school year.

1. :func:`build_decisions` — for every learner in a grade's class for the year,
   read their final marks (term results, CAPS weighting) and apply the CAPS
   promotion rule (``core.school.evaluate_promotion``) to get a *recommended*
   outcome. Existing decisions keep the outcome a teacher has already chosen.
2. :func:`decide` — the class teacher (or staff) records the outcome. A learner
   who is promoted / progressed / retained is **pre-registered** for the next
   year (an Application for year + 1, status ``preregistered``) with their
   details and parents carried over; Grade 12 completers and leavers are not.
3. :func:`confirm_returning` — the office confirms the learner is returning:
   the application is admitted and the January invoice (levy + January fees,
   no registration) is raised.
4. :func:`start_school_year` — in January: every admitted application for the
   year is enrolled in its grade and the year's class, last year's enrolments
   are closed, and any fees already paid for the new grade are applied.
"""
from django.db import transaction
from django.utils import timezone

from core import school

from .models import Application, Guardian, PromotionDecision

#: Application fields copied to the next year's (pre-)registration.
CARRY_FIELDS = (
    'id_document_type', 'id_number', 'passport_number', 'permit_number', 'document_expiry',
    'document_country', 'is_south_african', 'study_permit_number', 'study_permit_expiry',
    'permanent_residency', 'gender', 'physical_address', 'home_language', 'race', 'religion',
    'writing_hand', 'has_father', 'has_mother', 'lives_with', 'fee_payer', 'fee_payer_name',
    'fee_payer_can_afford', 'siblings_at_ucs', 'sibling_names', 'smsweb_number',
    'emergency_name', 'emergency_relationship', 'emergency_home_phone', 'emergency_cell_phone',
    'emergency_email', 'has_medical_condition', 'medical_conditions', 'medication',
    'medical_aid_name', 'medical_aid_number', 'medical_aid_plan', 'medical_aid_main_member',
    'medical_aid_main_member_phone', 'medical_aid_main_member_id', 'doctor_contact',
    'medical_expenses_name', 'medical_expenses_phone', 'medical_expenses_relationship',
    'media_consent', 'extramural_participation', 'office_account_number', 'office_pastel_account',
    'office_smsweb', 'office_learner_profile',
)


def class_for(programme, year):
    from apps.learning.models import Cohort
    cohort, _ = Cohort.objects.get_or_create(
        programme=programme, code=str(year),
        defaults={'name': f'{programme.display_name} · {year}'})
    return cohort


def learners_in(programme, year):
    """Active learners in ``programme``'s class for ``year`` (cohort code = year;
    learners with no class recorded are included for the current year)."""
    from apps.accounts.models import Person
    from django.db.models import Q
    flt = Q(programme_enrolments__programme=programme, programme_enrolments__is_active=True)
    year_filter = Q(programme_enrolments__cohort__code=str(year))
    if year == timezone.localdate().year:
        year_filter |= Q(programme_enrolments__cohort__isnull=True)
    return (Person.objects.filter(flt & year_filter).distinct()
            .select_related('user').order_by('last_name', 'first_name'))


def final_marks(person, programme, year):
    """``{subject code: final %}`` for the year — from the term results service
    when it is available, else from the computed subject grades."""
    try:
        from apps.reports.term_results import final_marks_for
        marks = final_marks_for(person.user, programme, year)
        if marks:
            return {code: float(pct) for code, pct in marks.items() if pct is not None}
    except ImportError:  # pragma: no cover - reports term results not installed
        pass
    from apps.reports.models import Grade
    return {g.module.code: float(g.final_pct) for g in
            Grade.objects.filter(student=person.user, module__programme=programme)
            .select_related('module')}


@transaction.atomic
def build_decisions(programme, year):
    """Create / refresh the promotion decision for every learner in the class."""
    made = []
    grade = programme.grade or 1
    for person in learners_in(programme, year):
        marks = final_marks(person, programme, year)
        result = school.evaluate_promotion(grade, marks) if marks else {
            'meets': False, 'outcome': PromotionDecision.OUTCOME_PENDING,
            'checks': [('Final marks recorded', False, 'no published marks yet')]}
        decision, _ = PromotionDecision.objects.get_or_create(
            person=person, year=year, defaults={'programme': programme})
        decision.programme = programme
        decision.final_marks = marks
        decision.checks = [list(check) for check in result['checks']]
        decision.recommended = result['outcome']
        decision.save()
        made.append(decision)
    return made


def next_programme(programme, outcome):
    from apps.learning.models import Programme
    if outcome in PromotionDecision.MOVES_UP:
        return Programme.objects.filter(institution=programme.institution,
                                        grade=(programme.grade or 0) + 1, is_active=True).first()
    if outcome == PromotionDecision.OUTCOME_RETAIN:
        return programme
    return None


@transaction.atomic
def preregister(decision):
    """Create / update the learner's application for the next year."""
    target = next_programme(decision.programme, decision.outcome)
    year = decision.year + 1
    if target is None:
        # Not coming back to a grade: withdraw a pre-registration made earlier.
        existing = Application.objects.filter(person=decision.person, year=year,
                                              status=Application.STATUS_PREREGISTERED).first()
        if existing is not None:
            existing.status = Application.STATUS_WITHDRAWN
            existing.save(update_fields=['status', 'updated_at'])
        decision.next_application = None
        decision.save(update_fields=['next_application', 'updated_at'])
        return None
    previous = Application.objects.filter(person=decision.person, year=decision.year).first()
    application, created = Application.objects.get_or_create(
        person=decision.person, year=year,
        defaults={'programme': target, 'status': Application.STATUS_PREREGISTERED,
                  'is_new_learner': False, 'previous': previous})
    if not created and application.status in (Application.STATUS_PREREGISTERED,
                                              Application.STATUS_WITHDRAWN):
        application.programme = target
        application.status = Application.STATUS_PREREGISTERED
    if previous is not None and created:
        for name in CARRY_FIELDS:
            setattr(application, name, getattr(previous, name))
        application.highest_grade_passed = (f'Grade {decision.programme.grade}'
                                            if decision.outcome in PromotionDecision.MOVES_UP
                                            else application.highest_grade_passed)
        application.year_grade_passed = (decision.year if decision.outcome in
                                         PromotionDecision.MOVES_UP else None)
    application.is_new_learner = False
    application.save()
    if previous is not None and created:
        for guardian in previous.guardians.all():
            Guardian.objects.get_or_create(application=application, role=guardian.role, defaults={
                field.name: getattr(guardian, field.name) for field in Guardian._meta.fields
                if field.name not in ('id', 'application', 'role', 'created_at', 'updated_at',
                                      'invite_sent_at')})
    decision.next_application = application
    decision.save(update_fields=['next_application', 'updated_at'])
    return application


def decide(decision, outcome, user, note=''):
    """Record the teacher's / staff decision and pre-register accordingly."""
    decision.outcome = outcome
    decision.note = note
    decision.decided_by = user
    decision.decided_at = timezone.now()
    decision.save()
    return preregister(decision)


@transaction.atomic
def confirm_returning(application, user):
    """The office confirms a pre-registered learner is returning: admit them and
    raise the January invoice (levy + January school fees)."""
    from . import services
    application.status = Application.STATUS_ADMITTED
    application.decided_by = user
    application.decided_at = timezone.now()
    application.submitted_at = application.submitted_at or timezone.now()
    application.save()
    invoice = services.raise_enrolment_invoice(application.person, application, [], months=1)
    return invoice


def subjects_for_next_year(person, programme, previous_programme):
    """The offerings a returning learner takes: compulsory subjects plus, in
    Grade 10 – 12, the same choices as last year where the subject continues."""
    from core.academic_spine import default_subjects
    offerings = list(programme.modules.filter(is_active=True).order_by('order', 'id'))
    if not any(o.subject_group for o in offerings):
        return offerings
    previous_codes = set()
    if previous_programme is not None:
        previous_codes = set(person.module_enrolments.filter(
            programme_module__programme=previous_programme).values_list('programme_module__code',
                                                                       flat=True))
    chosen = [o for o in offerings if not o.subject_group]
    for key, (_label, pick) in school.SUBJECT_GROUPS.items():
        group = [o for o in offerings if o.subject_group == key]
        kept = [o for o in group if o.code in previous_codes][:pick]
        if len(kept) < pick:
            defaults = [o for o in default_subjects(programme) if o.subject_group == key]
            kept += [o for o in defaults if o not in kept][:pick - len(kept)]
        chosen += kept
    return chosen


@transaction.atomic
def start_school_year(year, user=None):
    """Enrol every admitted application for ``year`` into its grade and the
    year's class; close last year's enrolments; apply fees already paid."""
    from apps.learning.fees import sync_paid_fees
    from apps.learning.models import ProgrammeEnrolment
    from core.academic_spine import enrol_student

    started = 0
    for application in (Application.objects.filter(year=year, status=Application.STATUS_ADMITTED)
                        .select_related('person', 'programme', 'previous__programme')):
        person, programme = application.person, application.programme
        if programme is None:
            continue
        cohort = class_for(programme, year)
        previous_programme = application.previous.programme if application.previous_id else None
        enrolment, modules = enrol_student(
            person, programme, cohort=cohort, activate=False,
            offerings=subjects_for_next_year(person, programme, previous_programme))
        enrolment.cohort = cohort
        enrolment.is_active = True
        enrolment.save(update_fields=['cohort', 'is_active', 'updated_at'])
        (ProgrammeEnrolment.objects.filter(person=person, is_active=True)
         .exclude(pk=enrolment.pk).update(is_active=False))
        person.enrolled_class = programme.display_name[:100]
        person.save(update_fields=['enrolled_class'])
        sync_paid_fees(person, programme)
        started += 1
    return started
