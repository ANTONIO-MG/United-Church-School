"""Who may open what, on a module.

The practice sells the same material two ways, and both have to be honoured on
one page:

* **Pay for the module** — a :class:`~apps.learning.models.ModuleEnrolment` that
  is ``active`` (paid & current) or on a live 7-day ``trial``. That opens
  *everything* in the module.
* **Buy one item** — a :class:`~apps.learning.models.ModuleMaterial` published to
  the shop as a ``shop.Product``. Buying it opens *that item only*, for someone
  who never paid for the module at all.

Neither side knows about the other, so this module is where they meet. The rule
a page needs is always the same question — "can this person open this row?" —
so views build one :class:`Gate` per request and ask it, rather than hitting the
database per material.

Staff, admins and the offering's own educators bypass the gate entirely: they
have to be able to see what they are building.

One thing this module deliberately does **not** decide is whether a candidate
has *earned* a row yet — whether they have read the guide before the mock, or
submitted their attempt before the solution opens. That is a teaching rule, not
a commercial one, and it lives in :mod:`apps.learning.sequence`. A page composes
the two: :class:`Gate` says "you may have this", the sequence gate says "not
yet", and a row needs both to open.
"""

import logging

logger = logging.getLogger('apps')

# Why a row is open, in the order the gate checks them. The reason is carried
# through to the template so a locked row can say something more useful than
# "locked" — "in your free week", "you bought this", "included in the module".
REASON_STAFF = 'staff'
REASON_EDUCATOR = 'educator'
REASON_FREE = 'free'
REASON_PREVIEW = 'preview'
REASON_TRIAL = 'trial'
REASON_PAID = 'paid'
REASON_PURCHASED = 'purchased'

REASON_LABELS = {
    REASON_STAFF: 'Staff access',
    REASON_EDUCATOR: 'You teach this module',
    REASON_FREE: 'Free module',
    REASON_PREVIEW: 'Free preview',
    REASON_TRIAL: 'Open during your free week',
    REASON_PAID: 'Included in your module',
    REASON_PURCHASED: 'You bought this item',
}

# Why a row is shut.
LOCK_UNPAID = 'unpaid'          # module not paid for, item not bought
LOCK_EXPIRED = 'expired'        # trial ran out / subscription lapsed
LOCK_EMBARGO = 'embargo'        # released later (available_from in the future)
LOCK_UNPUBLISHED = 'unpublished'
# Set by apps.learning.sequence, carried here so one MaterialState can express
# both verdicts and templates have a single thing to read.
LOCK_SEQUENCE = 'sequence'      # an earlier step in the week is not done
LOCK_SOLUTION = 'solution'      # the attempt has not been submitted yet


def purchased_product_ids(user):
    """IDs of every shop product this user has actually paid for and still holds.

    Reads paid orders rather than payments, because that is what the shop's own
    checkout writes; expired service lines (``OrderItem.expiry_date``) drop out,
    so a 30-day mock-paper pass stops opening the paper when it lapses.
    """
    if not getattr(user, 'is_authenticated', False):
        return set()
    try:
        from apps.shop.models import Order, OrderItem

        items = (OrderItem.objects
                 .filter(order__buyer=user, order__status=Order.STATUS_PAID)
                 .only('product_id', 'expiry_date'))
        return {item.product_id for item in items
                if item.product_id and not item.is_expired}
    except Exception:  # pragma: no cover — the shop is optional
        logger.exception('access: could not read purchased products')
        return set()


def is_staff_like(user):
    """Staff, superusers and anyone whose profile is admin/staff."""
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser or user.is_staff:
        return True
    return getattr(getattr(user, 'profile', None), 'user_type', '') in ('admin', 'staff')


class Gate:
    """One request's answer to "may this person open this?" for one offering.

    Built once per page load: it resolves the module-level verdict up front and
    caches the set of products the viewer owns, so asking about fifty materials
    costs no further queries.

        gate = Gate(request.user, offering)
        if gate.module_open: ...
        state = gate.for_material(material)      # → MaterialState
    """

    def __init__(self, user, offering, person=None):
        self.user = user
        self.offering = offering
        self.person = person if person is not None else getattr(user, 'profile', None)

        self.is_staff = is_staff_like(user)
        self.is_educator = self._teaches()
        self.enrolment = offering.enrolment_for(self.person) if self.person else None

        self.module_open, self.reason = self._resolve_module()
        # Only look up purchases when they could change an answer.
        self._owned = None

    # -- module level --------------------------------------------------------
    def _teaches(self):
        if self.person is None:
            return False
        try:
            return self.offering.educators.filter(pk=self.person.pk).exists()
        except Exception:  # pragma: no cover
            return False

    def _resolve_module(self):
        if self.is_staff:
            return True, REASON_STAFF
        if self.is_educator:
            return True, REASON_EDUCATOR
        if self.offering.is_free:
            return True, REASON_FREE
        enrolment = self.enrolment
        if enrolment is None:
            return False, LOCK_UNPAID
        if enrolment.is_trial_valid:
            return True, REASON_TRIAL
        if enrolment.is_unlocked:
            return True, REASON_PAID
        if enrolment.status in ('trial', 'expired'):
            return False, LOCK_EXPIRED
        return False, LOCK_UNPAID

    @property
    def can_author(self):
        """Staff and the offering's educators may add and edit material."""
        return self.is_staff or self.is_educator

    @property
    def owned_products(self):
        if self._owned is None:
            self._owned = purchased_product_ids(self.user)
        return self._owned

    @property
    def module_status_label(self):
        """What the module header says about access."""
        if self.module_open:
            return REASON_LABELS.get(self.reason, 'Open')
        if self.reason == LOCK_EXPIRED:
            return 'Access expired'
        return 'Locked — awaiting payment'

    # -- material level ------------------------------------------------------
    def for_material(self, material):
        """Resolve one material into a :class:`MaterialState`."""
        # Staff see everything, including drafts and embargoed items.
        if self.is_staff or self.is_educator:
            return MaterialState(material, True, REASON_STAFF if self.is_staff else REASON_EDUCATOR,
                                 visible=True)
        if not material.is_published:
            return MaterialState(material, False, LOCK_UNPUBLISHED, visible=False)
        if not material.is_released:
            return MaterialState(material, False, LOCK_EMBARGO, visible=True)
        if material.is_preview:
            return MaterialState(material, True, REASON_PREVIEW, visible=True)
        if self.module_open:
            return MaterialState(material, True, self.reason, visible=True)
        # Not in the module — but they may have bought this one item.
        if material.product_id and material.product_id in self.owned_products:
            return MaterialState(material, True, REASON_PURCHASED, visible=True)
        return MaterialState(material, False, self.reason, visible=True)

    def states_for(self, materials, *, sequence=None, week_materials=None):
        """``for_material`` across an iterable, dropping what must not be seen.

        Pass ``sequence`` (a :class:`apps.learning.sequence.SequenceGate`) and
        ``week_materials`` to apply the teaching order on top of the commercial
        verdict. A row that money opens can still be shut because the candidate
        has not sat the paper yet — and the state then carries *that* reason,
        because "submit your attempt to see the solution" is the useful message,
        not "locked".
        """
        rows = [self.for_material(m) for m in materials]
        if sequence is not None:
            scope = list(week_materials if week_materials is not None else materials)
            for row in rows:
                if not row.open:
                    continue                      # money already shut it
                is_open, reason = sequence.check(row.material, scope)
                if not is_open:
                    row.open = False
                    row.reason = reason
        return [row for row in rows if row.visible]


class MaterialState:
    """A material plus this viewer's verdict on it — what templates iterate."""

    # Not ``__slots__``-frozen on purpose: the sequence gate re-decides ``open``
    # and ``reason`` after the commercial gate has spoken.
    __slots__ = ('material', 'open', 'reason', 'visible')

    def __init__(self, material, is_open, reason, *, visible=True):
        self.material = material
        self.open = is_open
        self.reason = reason
        self.visible = visible

    def __repr__(self):  # pragma: no cover — debugging aid
        return f'<MaterialState {self.material_id} open={self.open} {self.reason}>'

    @property
    def material_id(self):
        return self.material.pk

    @property
    def locked(self):
        return not self.open

    @property
    def reason_label(self):
        if self.open:
            return REASON_LABELS.get(self.reason, '')
        from .sequence import SEQUENCE_LOCK_LABELS
        return {
            LOCK_EMBARGO: 'Released later',
            LOCK_EXPIRED: 'Your access has expired',
            LOCK_UNPAID: 'Unlock the module to open this',
            **SEQUENCE_LOCK_LABELS,
        }.get(self.reason, 'Locked')

    @property
    def url(self):
        """Where the row goes when it is open — always through the gated door.

        Never the material's own ``target_url``: a file's storage URL bypasses
        both gates and can be pasted into the cohort chat, which is exactly what
        the solution gate exists to prevent. :func:`apps.learning.material_open.
        material_open` re-asks both questions and *then* streams or redirects.
        """
        if not self.open:
            return ''
        from django.urls import reverse
        return reverse('learning:material-open', args=[self.material.pk])

    @property
    def is_sequence_lock(self):
        """Shut by the teaching order, not by money.

        Templates need the difference: a sequence lock is an instruction the
        candidate can act on right now, and must never be dressed up as a
        payment problem.
        """
        return self.locked and self.reason in (LOCK_SEQUENCE, LOCK_SOLUTION)

    @property
    def can_buy_single(self):
        """A locked row that is also sold on its own — offer the shop link.

        Never for a sequence lock: they already own it, they just have not
        earned it yet, and offering to sell it again would be nonsense.
        """
        return self.locked and not self.is_sequence_lock and self.material.is_purchasable
