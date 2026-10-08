"""The application for admission to United Church School.

One :class:`Application` per learner, filled in through the registration
wizard and processed by the school office. It is the online form of the *UCS
Application Form 2026* (``static/documents/``), section for section:

* page 1 — required documents (:class:`ApplicationDocument`), the SMSWEB
  contact number and the **office-use checklist** (the ``office_*`` fields);
* page 2 — the application for admission: grade applied for, the learner's
  identity document, general questions, both parents (:class:`Guardian`), an
  emergency contact and the previous school;
* pages 3 – 5 — indemnity, general consent and the medical form;
* pages 6 – 14 — terms & conditions, the learner's and parent's codes of
  conduct, the prospectus, fees, and consent for learner images and media;
* page 15 — acknowledgement of receipt of documents.

Every declaration a parent signs on paper is a recorded ``accept_*`` flag here,
stamped with who signed, when and from where (:meth:`Application.sign`).
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from core import validators as v
from core.storage import files_storage


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


YES_NO = [(True, 'Yes'), (False, 'No')]


class Application(TimeStampedModel):
    """A learner's application for admission to UCS."""

    STATUS_DRAFT = 'draft'
    STATUS_PREREGISTERED = 'preregistered'
    STATUS_SUBMITTED = 'submitted'
    STATUS_DOCUMENTS = 'documents'
    STATUS_REVIEW = 'review'
    STATUS_ADMITTED = 'admitted'
    STATUS_DECLINED = 'declined'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft — being completed'),
        (STATUS_PREREGISTERED, 'Pre-registered — awaiting confirmation the learner is returning'),
        (STATUS_SUBMITTED, 'Submitted — pending payment'),
        (STATUS_DOCUMENTS, 'Documents outstanding'),
        (STATUS_REVIEW, 'Under review by the office'),
        (STATUS_ADMITTED, 'Admitted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
    ]
    OPEN_STATUSES = (STATUS_DRAFT, STATUS_PREREGISTERED, STATUS_SUBMITTED, STATUS_DOCUMENTS,
                     STATUS_REVIEW)

    DOC_SA_ID = 'sa_id'
    DOC_BIRTH_CERT = 'birth_certificate'
    DOC_PASSPORT = 'passport'
    DOC_ASYLUM = 'asylum'
    ID_DOCUMENT_CHOICES = [
        (DOC_BIRTH_CERT, 'Unabridged birth certificate (up to Grade 9)'),
        (DOC_SA_ID, 'South African ID'),
        (DOC_PASSPORT, 'Valid passport'),
        (DOC_ASYLUM, 'Asylum seeker / refugee permit'),
    ]

    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female')]
    HAND_CHOICES = [('right', 'Right'), ('left', 'Left'), ('both', 'Both')]
    RACE_CHOICES = [
        ('', 'Prefer not to say'), ('african', 'African / Black'), ('coloured', 'Coloured'),
        ('indian', 'Indian / Asian'), ('white', 'White'), ('other', 'Other'),
    ]
    FEE_PAYER_CHOICES = [
        ('father', 'Father'), ('mother', 'Mother'), ('both', 'Both parents'),
        ('guardian', 'Guardian'), ('other', 'Someone else'),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    # One application per learner per school year: a returning learner is
    # pre-registered for the next year by the year-end promotion.
    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                               related_name='applications',
                               help_text='The learner this application is for.')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT,
                              db_index=True)
    year = models.PositiveSmallIntegerField(default=2026, db_index=True,
                                            help_text='The school year applied for.')

    # -- page 2: application for admission ------------------------------------
    programme = models.ForeignKey('learning.Programme', on_delete=models.SET_NULL, null=True,
                                  blank=True, related_name='applications',
                                  verbose_name='Grade applied for')
    is_new_learner = models.BooleanField(
        default=True, choices=YES_NO, verbose_name='New to UCS',
        help_text='No = already a UCS learner (no registration fee).')
    highest_grade_passed = models.CharField(max_length=20, blank=True)
    year_grade_passed = models.PositiveSmallIntegerField(null=True, blank=True,
                                                         verbose_name='Year when grade passed')

    # Identity document (as on ID / birth certificate / passport)
    id_document_type = models.CharField(max_length=20, choices=ID_DOCUMENT_CHOICES, blank=True,
                                        verbose_name='Which document does the learner hold?')
    id_number = models.CharField(max_length=30, blank=True,
                                 verbose_name='ID / birth certificate number')
    passport_number = models.CharField(max_length=30, blank=True)
    permit_number = models.CharField(max_length=40, blank=True,
                                     verbose_name='Asylum / refugee permit number')
    document_expiry = models.DateField(null=True, blank=True,
                                       verbose_name='Passport / permit expiry date')
    document_country = models.CharField(max_length=60, blank=True,
                                        verbose_name='Country of issue')
    is_south_african = models.BooleanField(default=True, choices=YES_NO,
                                           verbose_name='South African citizen')
    study_permit_number = models.CharField(max_length=40, blank=True)
    study_permit_expiry = models.DateField(null=True, blank=True)
    permanent_residency = models.BooleanField(
        default=False, verbose_name='Permanent residency or refugee status',
        help_text='Tick if the learner holds permanent residency or refugee status.')

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    physical_address = models.TextField(blank=True)
    home_language = models.CharField(max_length=60, blank=True)
    race = models.CharField(max_length=12, choices=RACE_CHOICES, blank=True,
                            help_text='Collected for Department of Education statistics only.')
    religion = models.CharField(max_length=60, blank=True)
    writing_hand = models.CharField(max_length=8, choices=HAND_CHOICES, blank=True,
                                    verbose_name='With which hand does the learner write?')

    # General
    has_father = models.BooleanField(null=True, blank=True, choices=YES_NO,
                                     verbose_name='Does the learner have a father?')
    has_mother = models.BooleanField(null=True, blank=True, choices=YES_NO,
                                     verbose_name='Does the learner have a mother?')
    lives_with = models.CharField(max_length=120, blank=True,
                                  verbose_name='Who does the learner live with?')
    fee_payer = models.CharField(max_length=10, choices=FEE_PAYER_CHOICES, blank=True,
                                 verbose_name='Who is responsible for paying the school fees?')
    fee_payer_name = models.CharField(max_length=120, blank=True,
                                      verbose_name='Name of the person paying the fees',
                                      help_text='If it is not the person the learner lives with.')
    fee_payer_can_afford = models.BooleanField(
        null=True, blank=True, choices=YES_NO, verbose_name='Can that person afford the school fees?')
    siblings_at_ucs = models.PositiveSmallIntegerField(
        default=0, verbose_name='Siblings at UCS',
        help_text='Brothers or sisters already at UCS (a 5% sibling discount applies to school fees '
                  'from the second child).')
    sibling_names = models.CharField(max_length=200, blank=True,
                                     verbose_name="Siblings' names and grades")
    smsweb_number = models.CharField(
        max_length=30, blank=True, verbose_name='SMSWEB contact number',
        help_text='The number the school sends SMS notifications to. It is your responsibility to '
                  'keep it correct; ask the office to add a second parent.')

    # Previous school
    previous_school = models.CharField(max_length=160, blank=True)
    previous_school_address = models.CharField(max_length=255, blank=True)
    previous_school_phone = models.CharField(max_length=30, blank=True,
                                             verbose_name='Previous school contact number')

    # Emergency contact (friend or relative)
    emergency_name = models.CharField(max_length=120, blank=True, verbose_name='Emergency contact name')
    emergency_relationship = models.CharField(max_length=60, blank=True,
                                              verbose_name='Relationship to the learner')
    emergency_home_phone = models.CharField(max_length=30, blank=True, verbose_name='Home number')
    emergency_cell_phone = models.CharField(max_length=30, blank=True, verbose_name='Cell number')
    emergency_email = models.EmailField(blank=True, verbose_name='E-mail')

    # -- pages 3 – 5: medical ---------------------------------------------------
    has_medical_condition = models.BooleanField(
        default=False, choices=YES_NO,
        verbose_name='Does the learner have a medical condition or allergy?')
    medical_conditions = models.TextField(
        blank=True, verbose_name='Illnesses, allergies and medical problems',
        help_text='e.g. asthma, epilepsy, heart conditions, allergies.')
    medication = models.TextField(blank=True, verbose_name='Medication that must be taken')
    medical_aid_name = models.CharField(max_length=100, blank=True, verbose_name='Medical aid')
    medical_aid_number = models.CharField(max_length=40, blank=True)
    medical_aid_plan = models.CharField(max_length=60, blank=True, verbose_name='Plan')
    medical_aid_main_member = models.CharField(max_length=120, blank=True, verbose_name='Main member')
    medical_aid_main_member_phone = models.CharField(max_length=30, blank=True,
                                                     verbose_name='Main member contact number')
    medical_aid_main_member_id = models.CharField(max_length=30, blank=True,
                                                  verbose_name='Main member ID / passport number')
    doctor_contact = models.CharField(
        max_length=200, blank=True, verbose_name='Medical practitioner',
        help_text='Name and number of the doctor to contact for medical history if necessary.')
    medical_expenses_name = models.CharField(
        max_length=120, blank=True, verbose_name='Person responsible for medical expenses')
    medical_expenses_phone = models.CharField(max_length=30, blank=True, verbose_name='Their contact number')
    medical_expenses_relationship = models.CharField(max_length=60, blank=True,
                                                     verbose_name='Relationship')

    # -- declarations ------------------------------------------------------------
    accept_terms = models.BooleanField(
        default=False, verbose_name='Terms & Conditions of contract',
        help_text='I have read and accept the Terms & Conditions, which form the contract between '
                  'me and UCS for the duration of my child\'s schooling.')
    accept_indemnity = models.BooleanField(
        default=False, verbose_name='Indemnity and consent',
        help_text='I consent to my child taking part in the extra-mural programme, sports days, '
                  'outings and excursions, accept the indemnity, and authorise UCS staff to consent '
                  'to emergency medical treatment at my expense if I cannot be reached.')
    extramural_participation = models.BooleanField(
        default=True, verbose_name='Extra-mural programme (Thursdays 13h30 – 15h00)',
        help_text='Untick if your child will NOT take part — they are then dismissed at 13h30 on '
                  'Thursdays.')
    accept_learner_code = models.BooleanField(
        default=False, verbose_name="Learner's code of conduct",
        help_text='The learner has read and agrees to the Learner\'s Code of Conduct.')
    accept_parent_code = models.BooleanField(
        default=False, verbose_name="Parent's code of conduct",
        help_text='I have read and agree to the Parent\'s Code of Conduct.')
    accept_prospectus = models.BooleanField(
        default=False, verbose_name='Prospectus, uniform and school rules',
        help_text='I have read the prospectus, including school times, uniform and dress code, '
                  'discipline and drug-testing policy.')
    accept_fees = models.BooleanField(
        default=False, verbose_name='Fees and affordability',
        help_text='I declare that I can afford the fees at United Church School, that fees are paid '
                  'in advance on the 1st of each month over 12 months, and that should I default I '
                  'will be handed over to the designated debt collectors.')
    accept_popia = models.BooleanField(
        default=False, verbose_name='Personal information (POPIA)',
        help_text='I consent to the school collecting, storing and updating my and my child\'s '
                  'personal information under the Protection of Personal Information Act, 2013.')
    media_consent = models.BooleanField(
        default=True, verbose_name='Learner images and media',
        help_text='UCS may use photos, video and audio of my child in school publications, the '
                  'website, marketing material and official social media. Untick to withhold consent.')
    acknowledge_documents = models.BooleanField(
        default=False, verbose_name='Acknowledgement of receipt of documents',
        help_text='I have received the terms and conditions, both codes of conduct, the prospectus, '
                  'the Fees 2026 schedule and the stationery & textbook list.')

    signed_by = models.CharField(max_length=120, blank=True,
                                 verbose_name='Full name of parent / guardian signing')
    signed_relationship = models.CharField(max_length=60, blank=True,
                                           verbose_name='Relationship to the learner')
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_ip = models.GenericIPAddressField(null=True, blank=True)
    signed_device = models.CharField(max_length=300, blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    invoice_uid = models.UUIDField(null=True, blank=True,
                                   help_text='public_id of the registration invoice.')
    months_prepaid = models.PositiveSmallIntegerField(
        default=1, help_text='Months of school fees paid in advance on enrolment.')
    previous = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='next_year',
                                 help_text="Last year's application (returning learners).")

    # -- office use only (page 1) ------------------------------------------------
    office_account_number = models.CharField(max_length=40, blank=True, verbose_name='ACC No')
    office_pastel_account = models.BooleanField(default=False,
                                                verbose_name='Account created on Pastel')
    office_smsweb = models.BooleanField(default=False, verbose_name='Added to SMSWEB')
    office_learner_profile = models.BooleanField(
        default=False, verbose_name='Learner profile (SA-SAMS, SA learners only)')
    office_transfer_received = models.BooleanField(
        default=False, verbose_name='Transfer card and final report received from previous school')
    office_letter_date = models.DateField(null=True, blank=True, verbose_name='Letter date')
    office_notes = models.TextField(blank=True)
    registrar = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  blank=True, related_name='+', verbose_name='Registrar')
    registrar_signed_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+',
                                   verbose_name='Deputy approval of admission')
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-year', '-submitted_at', '-created_at']
        verbose_name = 'Application for admission'
        verbose_name_plural = 'Applications for admission'
        constraints = [models.UniqueConstraint(fields=['person', 'year'],
                                               name='uniq_application_per_learner_per_year')]

    def __str__(self):
        grade = self.programme.display_name if self.programme_id else 'grade not chosen'
        return f'{self.learner_name} · {grade} · {self.get_status_display()}'

    # -- convenience ---------------------------------------------------------
    @property
    def learner_name(self):
        person = self.person
        name = f'{person.first_name} {person.last_name}'.strip()
        return name or (person.user.email if person.user_id else f'Applicant {self.pk}')

    @property
    def grade(self):
        return self.programme.grade if self.programme_id else None

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    @property
    def father(self):
        return self.guardians.filter(role=Guardian.ROLE_FATHER).first()

    @property
    def mother(self):
        return self.guardians.filter(role=Guardian.ROLE_MOTHER).first()

    @property
    def declarations_complete(self):
        return all(getattr(self, name) for name in REQUIRED_DECLARATIONS) and bool(self.signed_by)

    def required_document_kinds(self):
        """The documents this learner's application must carry (page 1):
        grade- and nationality-dependent."""
        grade = self.grade
        kinds = [ApplicationDocument.KIND_PHOTO]
        if grade is not None and grade >= 10:
            # "Grade 10 – 12 requires an ID, passport or asylum document."
            kinds.append(ApplicationDocument.KIND_ID)
        else:
            kinds.append(ApplicationDocument.KIND_BIRTH_CERT if self.is_south_african
                         else ApplicationDocument.KIND_ID)
        if grade is not None and grade <= 3:
            kinds.append(ApplicationDocument.KIND_CLINIC_CARD)
        if not self.is_south_african:
            kinds.append(ApplicationDocument.KIND_STUDY_PERMIT)
        if grade != 1 or self.previous_school:
            kinds.append(ApplicationDocument.KIND_REPORT)
        if self.previous_school and self.is_new_learner:
            kinds.append(ApplicationDocument.KIND_TRANSFER)
        kinds += [ApplicationDocument.KIND_PARENT_ID, ApplicationDocument.KIND_PAYSLIP]
        return kinds

    def missing_documents(self):
        held = set(self.documents.values_list('kind', flat=True))
        labels = dict(ApplicationDocument.KIND_CHOICES)
        return [(kind, labels[kind]) for kind in self.required_document_kinds() if kind not in held]

    def sign(self, request, name, relationship=''):
        """Record the electronic signature on the declarations."""
        self.signed_by = name
        self.signed_relationship = relationship
        self.signed_at = timezone.now()
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        self.signed_ip = (forwarded.split(',')[0].strip() if forwarded
                          else request.META.get('REMOTE_ADDR')) or None
        self.signed_device = request.META.get('HTTP_USER_AGENT', '')[:300]


#: Declarations that must be accepted before an application can be submitted.
REQUIRED_DECLARATIONS = (
    'accept_terms', 'accept_indemnity', 'accept_learner_code', 'accept_parent_code',
    'accept_prospectus', 'accept_fees', 'accept_popia', 'acknowledge_documents',
)


class Guardian(TimeStampedModel):
    """A parent or guardian on an application (page 2 — father, mother)."""
    ROLE_FATHER = 'father'
    ROLE_MOTHER = 'mother'
    ROLE_GUARDIAN = 'guardian'
    ROLE_CHOICES = [(ROLE_FATHER, 'Father'), (ROLE_MOTHER, 'Mother'),
                    (ROLE_GUARDIAN, 'Legal guardian')]
    TITLE_CHOICES = [('', '—'), ('Mr', 'Mr'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Miss', 'Miss'),
                     ('Dr', 'Dr'), ('Prof', 'Prof'), ('Pastor', 'Pastor'), ('Rev', 'Rev')]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='guardians')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    full_name = models.CharField(max_length=160, verbose_name='Full name and surname')
    id_number = models.CharField(max_length=30, blank=True, verbose_name='ID / passport number')
    home_phone = models.CharField(max_length=30, blank=True, verbose_name='Home number')
    work_phone = models.CharField(max_length=30, blank=True, verbose_name='Work number')
    cell_phone = models.CharField(max_length=30, blank=True, verbose_name='Cell number')
    email = models.EmailField(blank=True)
    residential_address = models.TextField(blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=120, blank=True)
    employer_phone = models.CharField(max_length=30, blank=True, verbose_name='Employer contact number')
    invite_sent_at = models.DateTimeField(
        null=True, blank=True, help_text='When this parent was invited to a linked parent account.')

    class Meta:
        ordering = ['application', 'role']
        constraints = [models.UniqueConstraint(fields=['application', 'role'],
                                               name='uniq_guardian_role_per_application')]

    def __str__(self):
        return f'{self.get_role_display()}: {self.full_name}'


class ApplicationDocument(TimeStampedModel):
    """A supporting document uploaded with an application (page 1 checklist).

    Stored on the private file server and only served to the office and the
    learner's own account (:func:`apps.admissions.views.document_file`)."""
    KIND_PHOTO = 'photo'
    KIND_BIRTH_CERT = 'birth_certificate'
    KIND_ID = 'id_document'
    KIND_CLINIC_CARD = 'clinic_card'
    KIND_STUDY_PERMIT = 'study_permit'
    KIND_REPORT = 'report_card'
    KIND_TRANSFER = 'transfer_card'
    KIND_PARENT_ID = 'parent_id'
    KIND_PAYSLIP = 'payslip'
    KIND_RESIDENCY = 'residency'
    KIND_OTHER = 'other'
    KIND_CHOICES = [
        (KIND_PHOTO, 'Learner ID photo'),
        (KIND_BIRTH_CERT, 'Birth certificate'),
        (KIND_ID, 'Learner ID / passport / asylum document'),
        (KIND_CLINIC_CARD, 'Clinic card (Grade 1 – 3)'),
        (KIND_STUDY_PERMIT, 'Study permit'),
        (KIND_REPORT, 'Most recent report card'),
        (KIND_TRANSFER, 'Transfer card (SA-SAMS report or non-SA transfer card)'),
        (KIND_PARENT_ID, 'Copy of parent ID / passport'),
        (KIND_PAYSLIP, 'Copy of parent payslip (confidential)'),
        (KIND_RESIDENCY, 'Permanent residency or refugee status'),
        (KIND_OTHER, 'Other supporting document'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, db_index=True)
    file = models.FileField(upload_to='admissions/%Y/%m/', storage=files_storage,
                            validators=v.validate_attachment)
    original_name = models.CharField(max_length=255, blank=True)
    expiry_date = models.DateField(null=True, blank=True,
                                   help_text='For a passport or permit, its expiry date.')
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    blank=True, related_name='+')
    verified_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['application', 'kind', '-created_at']

    def __str__(self):
        return f'{self.get_kind_display()} — {self.original_name or self.file.name}'


class PromotionDecision(TimeStampedModel):
    """The year-end decision for one learner in one grade (CAPS promotion).

    :attr:`recommended` is what the promotion rule (core.school.
    evaluate_promotion) says from the learner's final marks; :attr:`outcome` is
    what the class teacher (or staff) decides. Promoted and retained learners
    are pre-registered for the next year (:attr:`next_application`); the office
    confirms each one once it knows the learner is returning.
    """
    OUTCOME_PENDING = 'pending'
    OUTCOME_PROMOTE = 'promote'
    OUTCOME_PROGRESS = 'progress'
    OUTCOME_RETAIN = 'retain'
    OUTCOME_COMPLETE = 'complete'
    OUTCOME_LEAVING = 'leaving'
    OUTCOME_CHOICES = [
        (OUTCOME_PENDING, 'Not decided yet'),
        (OUTCOME_PROMOTE, 'Promoted to the next grade'),
        (OUTCOME_PROGRESS, 'Progressed (condoned) to the next grade'),
        (OUTCOME_RETAIN, 'Retained in the same grade'),
        (OUTCOME_COMPLETE, 'Completed Grade 12'),
        (OUTCOME_LEAVING, 'Leaving the school'),
    ]
    MOVES_UP = (OUTCOME_PROMOTE, OUTCOME_PROGRESS)

    person = models.ForeignKey('accounts.Person', on_delete=models.CASCADE,
                               related_name='promotion_decisions')
    programme = models.ForeignKey('learning.Programme', on_delete=models.CASCADE,
                                  related_name='promotion_decisions', verbose_name='Grade')
    year = models.PositiveSmallIntegerField(db_index=True)
    final_marks = models.JSONField(default=dict, blank=True,
                                   help_text='{subject code: final %} used for the decision.')
    checks = models.JSONField(default=list, blank=True,
                              help_text='The promotion requirements and whether each was met.')
    recommended = models.CharField(max_length=10, choices=OUTCOME_CHOICES, default=OUTCOME_PENDING)
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, default=OUTCOME_PENDING,
                               db_index=True)
    note = models.TextField(blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name='+')
    decided_at = models.DateTimeField(null=True, blank=True)
    next_application = models.ForeignKey(Application, on_delete=models.SET_NULL, null=True,
                                         blank=True, related_name='promotion_decisions')

    class Meta:
        ordering = ['programme__grade', 'person__last_name', 'person__first_name']
        constraints = [models.UniqueConstraint(fields=['person', 'year'],
                                               name='uniq_promotion_decision_per_year')]

    def __str__(self):
        return f'{self.person} · {self.programme} {self.year}: {self.get_outcome_display()}'
