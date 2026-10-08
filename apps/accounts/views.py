"""HTML pages for the accounts community area.

These render profile/about-me, settings, onboarding registration and the
admin/staff member-management pages inside the existing dashboard layout
(``myhub/elements/layouts/admin.html``):

* ``my_profile`` / ``profile`` / ``member_profile`` — the "About me" profile page.
* ``settings`` — edit your own profile.
* ``register`` — one-shot onboarding (role + profile + course enrolment).
* ``manage_members`` / ``member_enrol`` — admin/staff set a person's course +
  which of its modules they belong to.
"""

import logging

from django.conf import settings as dj_settings  # aliased: this module has a `settings` VIEW
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone, translation
from django.views.decorators.http import require_POST

from core.branding import t
from core.errors import capture, note, report
from core.roles import role_flags

from . import emails, forms, models, registration_billing, services


def _person_for(user):
    return getattr(user, 'profile', None)


def _require_admin_staff(request):
    """Return True if the current user may manage other people's enrolment."""
    return role_flags(request).get('is_admin_staff', False)


def enrolled_programmes(person):
    """The programmes a person is registered for, most recent registration first.

    Read off :class:`apps.learning.models.ProgrammeEnrolment` — the academic
    spine — not off the retired ``Person.course`` / ``Person.courses`` fields.
    A candidate registers for an institution's programme and its modules; there
    is no such thing as a course on this platform.
    """
    if person is None:
        return []
    from apps.learning.models import ProgrammeEnrolment
    return [
        row.programme for row in (
            ProgrammeEnrolment.objects
            .filter(person=person)
            .select_related('programme__institution', 'cohort')
            .order_by('-created_at'))
    ]


@login_required
def my_programmes(request):
    """The "My Programme(s)" nav target. Routes by how many the candidate is on:

    * 0 → send them to registration.
    * 1 → straight to their modules, which is what they came to open.
    * 2+ → a list page to pick from.
    """
    person = _person_for(request.user)
    programmes = enrolled_programmes(person)

    if not programmes:
        note('USER-4001', request, reason='no-enrolment')
        messages.info(request, "You're not registered for a programme yet.")
        return redirect('accounts:register-course')
    if len(programmes) == 1:
        return redirect('learning:my-modules')
    return render(request, 'accounts/my-programmes.html', {'programmes': programmes})


# ---------------------------------------------------------------------------
# Onboarding: registration (step 1) → profile completion (step 2)
# Gated by apps.accounts.middleware.OnboardingMiddleware until both are done.
# ---------------------------------------------------------------------------
def _create_enrolment_invoice(user, obj, amount):
    """Create a finance Invoice + a single line item for an enrolment."""
    from decimal import Decimal

    from apps.finance.models import Invoice, InvoiceItem
    invoice = Invoice.objects.create(customer=user, created_by=user, status=Invoice.STATUS_SENT)
    InvoiceItem.objects.create(
        invoice=invoice, description=f'Enrolment — {obj}'[:255],
        quantity=1, unit_price=Decimal(str(amount or 0)),
    )
    invoice.recalc_total()
    invoice.refresh_status()
    return invoice


# ---- 3-step registration wizard -------------------------------------------
# Step 1 (register)         → personal detail, saved to Person + side-tables.
# Step 2 (register_course)  → pick a course (+ add-ons) or products; → session.
# Step 3 (register_review)  → review, confirm, create the invoice → checkout.
# All three live under /accounts/ which is exempt from OnboardingMiddleware, so
# the user can move back and forth without being bounced to step 1.
def _client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _related_or_none(person, attr):
    """A Person's reverse-OneToOne side-table, or None if not created yet."""
    try:
        return getattr(person, attr)
    except Exception:
        return None


def _step1_forms(person, data=None, files=None):
    """The grouped Step-1 sections — each a dict with a form bound to the Person
    or its side-table, plus accordion metadata (title/icon/open)."""
    built = []
    for key, form_cls, attr, title, icon, is_open in forms.WIZARD_STEP1_FORMS:
        instance = person if attr is None else _related_or_none(person, attr)
        built.append({
            'key': key, 'form': form_cls(data, files, instance=instance, prefix=key),
            'title': title, 'icon': icon, 'open': is_open,
        })
    return built


def _create_registration_invoice(user, line_items):
    """One finance Invoice with a line per (label, amount) — course, add-ons,
    materials and any products the wizard collected."""
    from decimal import Decimal

    from apps.finance.models import Invoice, InvoiceItem
    invoice = Invoice.objects.create(customer=user, created_by=user, status=Invoice.STATUS_SENT)
    for label, amount in line_items:
        InvoiceItem.objects.create(
            invoice=invoice, description=str(label)[:255],
            quantity=1, unit_price=Decimal(str(amount or 0)),
        )
    invoice.recalc_total()
    invoice.refresh_status()
    return invoice


def _get_or_create_consent(person):
    consent, _ = models.PersonConsent.objects.get_or_create(person=person)
    return consent


def _serialize_person(person):
    """A JSON-able snapshot of everything we hold about a person (POPIA right of
    access). File fields are referenced by name only, not dumped."""
    from django.forms.models import model_to_dict
    exclude = ['id', 'person', 'user', 'profile_picture']

    def dump(obj):
        return model_to_dict(obj, exclude=exclude) if obj is not None else None

    return {
        'account': {
            'email': person.user.email,
            'username': person.user.get_username(),
            'date_joined': person.user.date_joined,
        },
        'profile': dump(person),
        'contact': dump(_related_or_none(person, 'contact')),
        'study_profile': dump(_related_or_none(person, 'study_profile')),
        'consent': dump(_related_or_none(person, 'consent')),
    }


@login_required
def register(request):
    """Step 1 — personal detail. Saved to Person + the grouped side-tables so
    the wizard can be resumed; only the lean fields are required. Marks
    ``profile_status`` so the data persists, then advances to course selection."""
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    if person.onboarding_complete:
        return redirect('myhub:index')
    # Invited parents get their own single-page registration; a team member
    # (admin/staff/educator) does a lean personal-details registration with no
    # institution/programme; the 3-step wizard below is for students only.
    if person.user_type == 'parent':
        return redirect('accounts:register-parent')
    if person.user_type == 'educator' and person.invite_id:
        return redirect('accounts:register-educator')
    if person.user_type in ('admin', 'staff', 'educator'):
        return redirect('accounts:register-staff')
    if person.pending_invoice_uid and not person.enrolment_settled:
        return redirect('accounts:enrol-checkout')

    sections = _step1_forms(person, request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if all(s['form'].is_valid() for s in sections):
            for s in sections:
                key, f = s['key'], s['form']
                obj = f.save(commit=False)
                if key == 'basics':
                    obj.profile_status = True
                    gemail = (f.cleaned_data.get('guardian_email') or '').strip()
                    obj.guardian_emails = [gemail] if gemail else []
                    obj.save()
                else:
                    obj.person = person
                    if key == 'consent':
                        obj.consent_date = timezone.now()
                        obj.consent_version = models.CONSENT_VERSION
                        obj.consent_ip = _client_ip(request)
                        obj.consent_device = request.META.get('HTTP_USER_AGENT', '')[:300]
                    obj.save()
            return redirect('accounts:register-course')
        messages.error(request, 'Please complete the required fields highlighted below.')

    return render(request, 'accounts/register/step1.html', {
        'page_title': 'Registration', 'person': person, 'sections': sections, 'step': 1,
    })


@login_required
def register_staff(request):
    """First-login profile for a team account (admin / staff / educator): the same
    lean personal details + POPIA as a student's step 1, but no institution or
    programme — a team member is not enrolled in anything. Completing it lifts the
    onboarding gate and sends the welcome pack."""
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    if person.onboarding_complete:
        return redirect('myhub:index')
    if person.user_type not in ('admin', 'staff', 'educator'):
        return redirect('accounts:register')

    sections = [s for s in _step1_forms(person, request.POST or None, request.FILES or None)
                if s['key'] in ('basics', 'contact', 'consent')]
    for section in sections:          # a learner's must-haves are optional for a team member
        if section['key'] == 'basics':
            for name in ('gender', 'date_of_birth'):
                section['form'].fields[name].required = False
    if request.method == 'POST':
        if all(s['form'].is_valid() for s in sections):
            for s in sections:
                key, f = s['key'], s['form']
                obj = f.save(commit=False)
                if key == 'basics':
                    obj.profile_status = True
                    obj.registered = True          # no enrolment step for team members
                    obj.guardian_emails = []
                    obj.save()
                else:
                    obj.person = person
                    if key == 'consent':
                        obj.consent_date = timezone.now()
                        obj.consent_version = models.CONSENT_VERSION
                        obj.consent_ip = _client_ip(request)
                        obj.consent_device = request.META.get('HTTP_USER_AGENT', '')[:300]
                    obj.save()
            try:
                from apps.communication.welcome import send_welcome_pack
                send_welcome_pack(request.user)
            except Exception:  # pragma: no cover - best-effort
                logging.getLogger('accounts').exception('accounts: welcome pack failed')
            messages.success(request, 'Welcome aboard — your profile is set up.')
            return redirect('myhub:index')
        messages.error(request, 'Please complete the required fields highlighted below.')

    return render(request, 'accounts/register/step1.html', {
        'page_title': 'Complete your profile', 'person': person,
        'sections': sections, 'step': 1, 'staff': True,
    })


@login_required
def staff_create(request):
    """Superuser only: create an admin / staff / educator account with a verified
    e-mail and a random password, and e-mail them an invitation with login details.
    They set their own password and complete their profile on first login."""
    if not request.user.is_superuser:
        messages.error(request, 'Only a superuser can create team accounts.')
        return redirect('myhub:index')

    form = forms.StaffAccountForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        from allauth.account.models import EmailAddress
        from django.contrib.auth import get_user_model
        from django.utils.crypto import get_random_string

        from . import emails
        cd = form.cleaned_data
        password = get_random_string(10)
        user = get_user_model().objects.create_user(
            username=cd['email'], email=cd['email'], password=password)
        # Verified from the moment they are created — they never see a verify step.
        EmailAddress.objects.update_or_create(
            user=user, email=cd['email'], defaults={'verified': True, 'primary': True})
        # The post-save signal creates the Person; fill in role + name.
        person = _person_for(user) or models.Person.objects.create(user=user)
        person.user_type = cd['user_type']
        person.first_name = cd['first_name']
        person.last_name = cd['last_name']
        person.registered = False        # completes the lean profile on first login
        person.profile_status = False
        person.save()
        emails.send_account_invitation(user, password, request)
        role_label = dict(forms.STAFF_ROLE_CHOICES).get(cd['user_type'], cd['user_type'])
        messages.success(
            request,
            f"{cd['first_name']} {cd['last_name']} created as {role_label}. "
            "An invitation with login details has been e-mailed.")
        return redirect('accounts:staff-create')

    recent = (models.Person.objects.filter(user_type__in=['admin', 'staff', 'educator'])
              .select_related('user').order_by('-user__date_joined')[:15])
    return render(request, 'accounts/staff_create.html', {
        'page_title': 'Create team account', 'form': form, 'recent': recent,
    })


def _application(person):
    from apps.admissions.services import application_for
    return application_for(person)


def _reg_programme(request):
    """The grade chosen on step 2 (from the session), or ``None``."""
    from apps.learning.models import Programme
    reg = request.session.get('reg') or {}
    if not reg.get('programme_id'):
        return None
    return (Programme.objects.filter(pk=reg['programme_id'], is_active=True)
            .select_related('institution').first())


def _grade_catalogue():
    """Every active grade with its fees and subjects, for the step-2 picker.

    Grouped by CAPS phase. Each subject carries its choice group (blank =
    compulsory) so the picker can show Grade 10 – 12's "choose one / choose
    three" rules; the same rules are enforced again on the server."""
    from apps.learning.models import Programme
    from core import school

    current_year = timezone.now().year
    grades = []
    for prog in (Programme.objects.filter(is_active=True, institution__is_active=True)
                 .select_related('institution')
                 .prefetch_related('modules__module', 'cohorts')
                 .order_by('grade', 'order', 'name')):
        cohort = (prog.cohorts.filter(is_active=True, code=str(current_year)).first()
                  or prog.cohorts.filter(is_active=True).order_by('-start_date', '-code').first())
        grades.append({
            'id': prog.pk, 'grade': prog.grade, 'name': prog.display_name,
            'level': prog.level, 'phase': prog.get_level_display(),
            'cohort_id': cohort.pk if cohort else 'year',
            'fees': {
                'registration': float(prog.registration_fee or 0),
                'levy': float(prog.annual_levy or 0),
                'monthly': float(prog.monthly_fee or 0),
                'annual': float(prog.annual_fees),
            },
        })
        subjects = [{'id': pm.pk, 'code': pm.code, 'name': pm.display_name,
                     'group': pm.subject_group or ''}
                    for pm in prog.modules.all() if pm.is_active]
        grades[-1]['compulsory'] = [x for x in subjects if not x['group']]
        grades[-1]['choice_groups'] = [
            {'key': key, 'label': label, 'pick': pick,
             'subjects': [x for x in subjects if x['group'] == key]}
            for key, (label, pick) in school.SUBJECT_GROUPS.items()
            if any(x['group'] == key for x in subjects)]
    groups = [{'key': key, 'label': label, 'pick': pick}
              for key, (label, pick) in school.SUBJECT_GROUPS.items()]
    return grades, groups


def _validate_subject_choice(programme, chosen_ids):
    """Compulsory subjects are always included; each choice group must have
    exactly its number picked. Returns ``(module_ids, errors)``."""
    from core import school

    offerings = list(programme.modules.filter(is_active=True))
    chosen = {int(i) for i in chosen_ids}
    ids, errors = [], []
    for pm in offerings:
        if not pm.subject_group:
            ids.append(pm.pk)
    for key, (label, pick) in school.SUBJECT_GROUPS.items():
        in_group = [pm for pm in offerings if pm.subject_group == key]
        if not in_group:
            continue
        picked = [pm.pk for pm in in_group if pm.pk in chosen]
        if len(picked) != pick:
            errors.append(f'{label.split(" — ")[0]}: please choose {pick}.')
        ids += picked
    return ids, errors


@login_required
def register_course(request):
    """Step 2 — the grade applied for and, for Grade 10 – 12, the subject
    choices. Compulsory subjects come with the grade. The fee schedule for the
    grade is shown live; the choice is held in the session and on the learner's
    application so going back keeps it."""
    person = _person_for(request.user)
    if person is None or not person.profile_status:
        return redirect('accounts:register')
    if person.onboarding_complete:
        return redirect('myhub:index')

    from apps.learning.models import Programme
    reg = request.session.get('reg', {})
    application = _application(person)

    if request.method == 'POST':
        if request.POST.get('nav') == 'back':
            return redirect('accounts:register')
        programme_id = (request.POST.get('programme_id') or '').strip()
        programme = (Programme.objects.filter(pk=programme_id, is_active=True).first()
                     if programme_id.isdigit() else None)
        chosen = [m for m in request.POST.getlist('module_ids') if m.isdigit()]
        if programme is not None:
            # "Choose one" groups post as radios named choice_<grade id>_<group>.
            prefix = f'choice_{programme.pk}_'
            chosen += [value for key, value in request.POST.items()
                       if key.startswith(prefix) and value.isdigit()]
        is_new = request.POST.get('is_new_learner', 'yes') != 'no'
        if programme is None:
            note('USER-1002', request, reason='no_programme')
            messages.error(request, 'Please choose the grade you are applying for.')
        else:
            module_ids, errors = _validate_subject_choice(programme, chosen)
            if errors:
                note('USER-1002', request, reason='subject_choice', programme=programme.pk)
                for error in errors:
                    messages.error(request, error)
            elif not module_ids:
                messages.error(request, 'This grade has no subjects set up yet — please contact '
                                        'the school office.')
            else:
                cohort_id = (request.POST.get('cohort_id') or '').strip()
                request.session['reg'] = {
                    'institution_id': programme.institution_id,
                    'programme_id': programme.pk,
                    'module_ids': module_ids,
                    'cohort_id': int(cohort_id) if cohort_id.isdigit() else (cohort_id or None),
                    'is_new_learner': is_new,
                }
                request.session.modified = True
                application.programme = programme
                application.is_new_learner = is_new
                application.save(update_fields=['programme', 'is_new_learner', 'updated_at'])
                person.enrolled_class = programme.display_name[:100]
                person.save(update_fields=['enrolled_class'])
                return redirect('accounts:register-family')
        reg = {'programme_id': int(programme_id) if programme_id.isdigit() else None,
               'module_ids': [int(m) for m in chosen], 'is_new_learner': is_new}

    grades, groups = _grade_catalogue()
    if not reg.get('programme_id') and application.programme_id:
        reg = {**reg, 'programme_id': application.programme_id,
               'is_new_learner': application.is_new_learner}
    return render(request, 'accounts/register/step2.html', {
        'page_title': 'Grade & subjects', 'person': person, 'reg': reg,
        'grades': grades, 'groups': groups, 'step': 2,
    })


@login_required
def register_family(request):
    """Step 3 — the learner's identity document and background, the parents /
    guardians, an emergency contact and the previous school (application form
    page 2)."""
    from apps.admissions import forms as aforms
    from apps.admissions import services as admissions
    from apps.admissions.models import Guardian

    person = _person_for(request.user)
    if person is None or not person.profile_status:
        return redirect('accounts:register')
    if person.onboarding_complete:
        return redirect('myhub:index')
    if _reg_programme(request) is None:
        return redirect('accounts:register-course')
    application = _application(person)

    data = request.POST or None
    learner_form = aforms.LearnerDetailsForm(data, instance=application, prefix='learner')
    general_form = aforms.GeneralForm(data, instance=application, prefix='general')
    emergency_form = aforms.EmergencyForm(data, instance=application, prefix='emergency')
    guardian_forms = [
        aforms.GuardianForm(data, instance=admissions.guardian_instance(application, role),
                            prefix=role, role=role)
        for role, _label in Guardian.ROLE_CHOICES
    ]
    forms_all = [learner_form, general_form, emergency_form, *guardian_forms]

    if request.method == 'POST':
        if request.POST.get('nav') == 'back':
            return redirect('accounts:register-course')
        valid = all(f.is_valid() for f in forms_all)
        if valid and all(g.is_blank for g in guardian_forms):
            valid = False
            messages.error(request, 'Please give the details of at least one parent or guardian.')
        if valid:
            learner_form.save(commit=False)
            general_form.save(commit=False)
            emergency_form.save(commit=False)
            application.gender = application.gender or person.gender or ''
            application.save()
            admissions.save_guardians(application, guardian_forms)
            return redirect('accounts:register-medical')
        if not messages.get_messages(request):
            messages.error(request, 'Please complete the required fields highlighted below.')

    return render(request, 'accounts/register/step_family.html', {
        'page_title': 'Learner & family', 'person': person, 'step': 3,
        'learner_form': learner_form, 'general_form': general_form,
        'emergency_form': emergency_form,
        'guardian_forms': list(zip(Guardian.ROLE_CHOICES, guardian_forms)),
    })


@login_required
def register_medical(request):
    """Step 4 — the medical form and the supporting documents (application form
    pages 1 and 5). Documents can also be added later under My application; an
    application with documents missing is marked "documents outstanding"."""
    from apps.admissions import forms as aforms
    from apps.admissions.models import ApplicationDocument

    person = _person_for(request.user)
    if person is None or not person.profile_status:
        return redirect('accounts:register')
    if person.onboarding_complete:
        return redirect('myhub:index')
    if _reg_programme(request) is None:
        return redirect('accounts:register-course')
    application = _application(person)

    medical_form = aforms.MedicalForm(request.POST or None, instance=application, prefix='medical')
    upload_errors = []
    if request.method == 'POST':
        if request.POST.get('nav') == 'back':
            return redirect('accounts:register-family')
        if medical_form.is_valid():
            medical_form.save()
            upload_errors = _save_uploaded_documents(request, application)
            if not upload_errors:
                return redirect('accounts:register-review')
        else:
            messages.error(request, 'Please complete the required fields highlighted below.')

    required = application.required_document_kinds()
    labels = dict(ApplicationDocument.KIND_CHOICES)
    held = {}
    for doc in application.documents.all():
        held.setdefault(doc.kind, []).append(doc)
    optional = [ApplicationDocument.KIND_RESIDENCY, ApplicationDocument.KIND_OTHER]
    document_rows = [{'kind': kind, 'label': labels[kind], 'required': kind in required,
                      'held': held.get(kind, [])}
                     for kind in required + [k for k in optional if k not in required]]
    return render(request, 'accounts/register/step_medical.html', {
        'page_title': 'Medical & documents', 'person': person, 'step': 4,
        'medical_form': medical_form, 'document_rows': document_rows,
        'upload_errors': upload_errors,
    })


def _save_uploaded_documents(request, application):
    """Store each ``doc_<kind>`` file posted on step 4 (or My application).
    Returns a list of error strings for files that failed validation."""
    from django.core.exceptions import ValidationError

    from apps.admissions.models import ApplicationDocument
    from core import validators as v

    errors = []
    kinds = dict(ApplicationDocument.KIND_CHOICES)
    for kind, label in kinds.items():
        upload = request.FILES.get(f'doc_{kind}')
        if not upload:
            continue
        try:
            for validator in v.validate_attachment:
                validator(upload)
        except ValidationError as exc:
            errors.append(f'{label}: {" ".join(exc.messages)}')
            continue
        expiry = (request.POST.get(f'expiry_{kind}') or '').strip() or None
        # One current copy per kind: an unverified earlier upload is replaced.
        if kind != ApplicationDocument.KIND_OTHER:
            application.documents.filter(kind=kind, verified=False).delete()
        ApplicationDocument.objects.create(application=application, kind=kind, file=upload,
                                           original_name=upload.name[:255], expiry_date=expiry)
    for error in errors:
        messages.error(request, error)
    return errors


@login_required
def register_review(request):
    """Step 5 — the declarations, the electronic signature and the fees.

    Finishes one of two ways: **pay now** (PayFast — card / instant EFT) or
    **pay by EFT / at the school office**. Either way the learner's subjects
    are registered and an invoice raised for registration (new learners), the
    annual levy and the first month's school fees; the subjects unlock when it
    is paid. "The application is pending until payment is received."
    """
    person = _person_for(request.user)
    if person is None or not person.profile_status:
        return redirect('accounts:register')
    reg = request.session.get('reg')
    if not reg or not reg.get('programme_id') or not reg.get('module_ids'):
        return redirect('accounts:register-course')

    from apps.admissions import forms as aforms
    from apps.admissions import services as admissions
    from apps.learning import enrolment as enrol
    from apps.learning.models import ProgrammeModule

    programme = _reg_programme(request)
    if programme is None:
        note('USER-3002', request, programme=reg.get('programme_id'))
        return redirect('accounts:register-course')
    modules = list(ProgrammeModule.objects.filter(
        pk__in=reg['module_ids'], programme=programme, is_active=True).select_related('module'))
    if not modules:
        note('USER-3002', request, programme=programme.pk, modules=reg.get('module_ids'))
        return redirect('accounts:register-course')
    application = _application(person)
    if not application.guardians.exists():
        return redirect('accounts:register-family')

    fees = admissions.fee_summary(programme, new_learner=application.is_new_learner,
                                  siblings=application.siblings_at_ucs)
    form = aforms.DeclarationsForm(request.POST or None, instance=application, prefix='decl')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'back':
            return redirect('accounts:register-medical')
        if form.is_valid():
            application = form.save(commit=False)
            application.sign(request, form.cleaned_data['signed_by'],
                             form.cleaned_data.get('signed_relationship', ''))
            application.save()

            enrolments = enrol.register_modules(
                person, programme, [m.pk for m in modules], cohort_id=reg.get('cohort_id'))
            person.registered = True
            try:
                from apps.communication.welcome import send_welcome_pack
                send_welcome_pack(request.user)
            except Exception:  # pragma: no cover - best-effort
                logging.getLogger('accounts').exception('accounts: welcome pack failed')

            with capture('FIN-8002', request):
                invoice = admissions.raise_enrolment_invoice(person, application, enrolments)
            admissions.submit(application)
            try:
                admissions.invite_guardians(application, invited_by=request.user)
            except Exception:  # pragma: no cover - best-effort
                logging.getLogger('accounts').exception('accounts: guardian invites failed')
            # Access is governed by subject locking, not the global onboarding
            # gate, so the family goes into the hub either way — with the
            # subjects open (paid) or locked (awaiting payment).
            person.pending_invoice_uid = None
            person.save(update_fields=['registered', 'pending_invoice_uid'])
            request.session.pop('reg', None)
            request.session.modified = True

            if invoice is None:  # a grade with no fees configured
                for e in enrolments:
                    e.activate(months=1)
                messages.success(request, 'Application submitted — your subjects are open.')
                return redirect('myhub:index')

            if action == 'eft':
                delivery = registration_billing.send_invoice_everywhere(invoice, person)
                registration_billing.send_registration_summary(
                    person, invoice, enrolments, paid=False, programme=programme)
                sent = ' and '.join(delivery['sent']) or 'your account'
                messages.success(
                    request,
                    f'Application submitted. Your invoice has been sent to {sent}. The application '
                    'is pending until payment is received — pay at Standard Bank using the '
                    "learner's name and grade as the reference, and e-mail the deposit slip to "
                    f"{t('brand.support_email', 'uchs@unitedcs.co.za')}.")
                if delivery['failed']:
                    messages.info(request, 'We could not reach you on '
                                           f'{" and ".join(delivery["failed"])} — the invoice is '
                                           'in your account under Finance either way.')
                return redirect(reverse('accounts:register-complete') + '?mode=eft')

            # action == 'pay' → PayFast; settling the invoice unlocks the subjects,
            # files the proof of payment and moves the application to review.
            return redirect('finance:pay', public_id=invoice.public_id)
        messages.error(request, 'Please accept each declaration and sign the application.')

    return render(request, 'accounts/register/step3.html', {
        'page_title': 'Agreements & fees', 'person': person, 'programme': programme,
        'modules': modules, 'fees': fees, 'application': application, 'form': form,
        'missing_documents': application.missing_documents(),
        'currency': 'ZAR', 'step': 5,
    })


#: The two ways registration finishes, and what the hand-off screen says about
#: each. ``paid`` is the PayFast route (money has cleared); ``eft`` is the
#: pay-by-EFT / school-office route, where the invoice is out.
REGISTRATION_OUTCOMES = {
    'paid': {
        'heading': 'Payment received',
        'detail': "Thank you — your payment came through and your child's subjects are open. "
                  'The school office will now review the application.',
        'note': 'A receipt and your application summary are on their way to your inbox.',
        'tone': 'success',
    },
    'eft': {
        'heading': 'Application submitted',
        'detail': 'Your application has been received. It is pending until payment is received — '
                  'the subjects open as soon as the invoice is paid.',
        'note': "Your invoice and application summary are on their way to your inbox. Pay at "
                "Standard Bank using the learner's name and grade as the reference, or at the "
                'school office (card only — no cash).',
        'tone': 'info',
    },
}

#: How long the hand-off screen holds before it forwards to the dashboard.
REGISTRATION_COMPLETE_SECONDS = 5


@login_required
def registration_complete(request):
    """The screen both payment routes land on before the dashboard.

    Previously each route redirected straight to ``myhub:index`` with a flash
    message, which meant the one moment the student most wants confirmed —
    "did my payment go through?" — arrived as a toast on a busy dashboard and
    was gone. This holds the outcome on its own screen for a few seconds, the
    way the post-login redirect does, then forwards.

    ``?mode=paid`` for the PayFast route, ``?mode=eft`` for EFT / the office.
    Unknown values fall back to the EFT copy, which claims the least.
    """
    mode = request.GET.get('mode', 'eft')
    outcome = REGISTRATION_OUTCOMES.get(mode) or REGISTRATION_OUTCOMES['eft']
    return render(request, 'accounts/register/complete.html', {
        'page_title': outcome['heading'],
        'outcome': outcome,
        'mode': mode,
        'seconds': REGISTRATION_COMPLETE_SECONDS,
        'next_url': reverse('myhub:index'),
    })


# ---------------------------------------------------------------------------
# Invite-based registration — parents/guardians/sponsors + educators
# ---------------------------------------------------------------------------
def accept_invite(request, token):
    """Public entry point for an invite link. Stashes the invite in the session
    and sends the visitor through the normal sign-up (create + verify account);
    sign-up then sets their role from the invite so they never pick a type. Once
    signed in, they land on their single-page role registration."""
    invite = (models.Invitation.objects
              .filter(token=token).select_related('student__user', 'programme').first())
    if invite is None or not invite.is_open:
        return render(request, 'accounts/invite-invalid.html', {'invite': invite}, status=410)

    # One e-mail address, one account. A parent invited on an address that is
    # already somebody's login cannot become a second account on it — that is
    # what the student would be typing when they mean their own address, or a
    # second parent re-using the first one's. Say so at the link, before they
    # fill in a sign-up form that could never have worked.
    User = get_user_model()
    existing = User.objects.filter(email__iexact=invite.email).first()
    if existing is not None and not (request.user.is_authenticated
                                     and request.user.pk == existing.pk):
        note('USER-2002', request, kind='invite-email-taken', role=invite.role)
        existing_person = getattr(existing, 'profile', None)
        return render(request, 'accounts/invite-invalid.html', {
            'invite': invite,
            'email_taken': True,
            'existing_role': (existing_person.get_user_type_display()
                              if existing_person else 'an account'),
        }, status=409)

    if request.user.is_authenticated:
        person = _person_for(request.user)
        if person and not person.onboarding_complete and person.user_type == invite.role:
            return redirect('accounts:register-parent' if invite.role == invite.ROLE_PARENT
                            else 'accounts:register-educator')
        return redirect('myhub:index')
    request.session['invite_token'] = str(invite.token)
    return redirect(f"{reverse('myhub:page-register')}?email={invite.email}")


@login_required
def register_parent(request):
    """Single-page registration for an invited parent/guardian/sponsor."""
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    if person.onboarding_complete:
        return redirect('myhub:index')
    if person.user_type != models.Invitation.ROLE_PARENT:
        return redirect('accounts:register')
    invite = person.invite
    student = invite.student if invite else None
    if request.method == 'POST':
        form = forms.ParentRegistrationForm(request.POST, instance=person)
        if form.is_valid():
            p = form.save(commit=False)
            p.profile_status = True
            p.registered = True
            if student:
                p.child_name = (f'{student.first_name} {student.last_name}'.strip()
                                or (student.user.email if student.user_id else ''))
            p.save()
            if student and student.user_id and models.ParentLink.can_add_parent(student.user):
                models.ParentLink.objects.get_or_create(
                    parent=request.user, student=student.user,
                    defaults={'relationship': form.cleaned_data.get('relationship', '')})
            if invite:
                invite.accept(request.user)
            try:
                emails.send_registration_summary(person)
            except Exception:
                pass
            messages.success(request, 'Registration complete — welcome aboard!')
            return redirect('myhub:index')
    else:
        form = forms.ParentRegistrationForm(instance=person)
    return render(request, 'accounts/register-parent.html', {
        'page_title': 'Register', 'form': form, 'student': student, 'person': person})


@login_required
def register_educator(request):
    """Single-page registration for an invited educator."""
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    if person.onboarding_complete:
        return redirect('myhub:index')
    if person.user_type != models.Invitation.ROLE_EDUCATOR:
        return redirect('accounts:register')
    invite = person.invite
    programme = invite.programme if invite else None
    if request.method == 'POST':
        form = forms.EducatorRegistrationForm(request.POST, instance=person)
        if form.is_valid():
            p = form.save(commit=False)
            p.profile_status = True
            p.registered = True
            if programme:
                p.enrolled_class = programme.name
            p.save()
            if programme:
                services.enrol_educator(person, programme)
            if invite:
                invite.accept(request.user)
            try:
                emails.send_registration_summary(person)
            except Exception:
                pass
            messages.success(request, 'Registration complete — welcome aboard!')
            return redirect('myhub:index')
    else:
        form = forms.EducatorRegistrationForm(instance=person)
    return render(request, 'accounts/register-educator.html', {
        'page_title': 'Register', 'form': form, 'programme': programme, 'person': person})


@login_required
def add_educator(request):
    """Admin/staff: invite an educator to a programme by e-mail."""
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to invite educators.')
        return redirect('myhub:index')
    if request.method == 'POST':
        form = forms.AddEducatorForm(request.POST)
        if form.is_valid():
            invite = models.Invitation.objects.create(
                role=models.Invitation.ROLE_EDUCATOR, email=form.cleaned_data['email'],
                programme=form.cleaned_data['programme'], invited_by=request.user)
            emails.send_invite(invite)
            messages.success(request, f'Invite sent to {invite.email} for {invite.programme}.')
            return redirect('accounts:manage-members')
    else:
        form = forms.AddEducatorForm()
    return render(request, 'accounts/add-educator.html', {'page_title': 'Add educator', 'form': form})


@login_required
def enrol_checkout(request):
    """Registration checkout — settle the enrolment invoice created during
    registration. Paid → PayFast (finance:pay). Free (0) → confirm here, which
    records a 0 payment + marks the invoice paid. Either way an invoice + a
    payment exist, and settling it lifts the onboarding gate."""
    person = _person_for(request.user)
    if person is None or not person.pending_invoice_uid:
        return redirect('myhub:index')
    invoice = person.get_pending_invoice()
    if invoice is None:
        person.pending_invoice_uid = None
        person.save(update_fields=['pending_invoice_uid'])
        return redirect('myhub:index')
    if invoice.status == invoice.STATUS_PAID:
        person.pending_invoice_uid = None
        person.save(update_fields=['pending_invoice_uid'])
        messages.success(request, 'Enrolment confirmed — welcome aboard!')
        return redirect('myhub:index')

    is_free = (invoice.total or 0) <= 0
    if request.method == 'POST':
        from apps.finance import services as finance_services
        if is_free:
            # Free enrolment still "goes through checkout": record a 0 payment,
            # then mark the invoice paid (refresh_status won't for a 0 total).
            finance_services.settle_payment(
                invoice, 0, method='free', gateway=invoice.payments.model.GATEWAY_MANUAL)
            invoice.status = invoice.STATUS_PAID
            invoice.save(update_fields=['status', 'updated_at'])
            # A 0-total invoice doesn't fire finance._on_invoice_paid, so unlock
            # what it was raised for and clear the onboarding gate directly.
            from apps.learning.enrolment import activate_modules_for_invoice
            activate_modules_for_invoice(invoice)
            person.pending_invoice_uid = None
            person.save(update_fields=['pending_invoice_uid'])
            messages.success(request, 'Enrolment confirmed — welcome aboard!')
            return redirect('myhub:index')
        # Paid → hand off to the PayFast pay page.
        return redirect('finance:pay', public_id=invoice.public_id)

    return render(request, 'accounts/enrol-checkout.html', {
        'page_title': 'Checkout', 'invoice': invoice, 'person': person,
        'is_free': is_free, 'item': invoice.items.first(),
    })


# ---------------------------------------------------------------------------
# Parent / guardian registration (via a student's invite link; max two)
# ---------------------------------------------------------------------------
def parent_register(request, token):
    """A parent registers against a specific student via their invite token.
    Open to anonymous visitors (the link is e-mailed/shared)."""
    student_person = get_object_or_404(models.Person, parent_invite_token=token)
    student_user = student_person.user
    User = get_user_model()
    error = None
    full = not models.ParentLink.can_add_parent(student_user)

    if request.method == 'POST' and not full:
        if request.user.is_authenticated:
            parent_user = request.user
        else:
            email = (request.POST.get('email') or '').strip()
            password = request.POST.get('password') or ''
            first = (request.POST.get('first_name') or '').strip()
            last = (request.POST.get('last_name') or '').strip()
            if not email or not password:
                error = 'E-mail and password are required.'
            elif (User.objects.filter(email__iexact=email).exists()
                  or User.objects.filter(username__iexact=email).exists()):
                error = 'An account with that e-mail already exists — sign in first, then open this link.'
            else:
                parent_user = User.objects.create_user(username=email, email=email, password=password)
                profile = getattr(parent_user, 'profile', None) or models.Person.objects.create(user=parent_user)
                profile.user_type = 'parent'
                profile.first_name = first
                profile.last_name = last
                profile.child_name = student_user.get_full_name() or student_user.get_username()
                profile.save()
                # E-mail verification (so they can sign in) — reuse MyHub's helper.
                try:
                    from apps.myhub.views import _send_verification_email
                    _send_verification_email(request, parent_user, signup=True)
                except Exception:
                    pass

        if error is None:
            if not models.ParentLink.can_add_parent(student_user):
                full = True
            else:
                models.ParentLink.objects.get_or_create(parent=parent_user, student=student_user)
                if request.user.is_authenticated:
                    messages.success(request, f'You are now linked as a guardian of {student_user}.')
                    return redirect('myhub:index')
                messages.success(request, 'Account created — please verify your e-mail, then sign in.')
                return redirect('myhub:page-login')

    return render(request, 'accounts/parent-register.html', {
        'page_title': 'Parent registration',
        'student': student_user, 'student_person': student_person,
        'full': full, 'error': error,
        'max_parents': models.ParentLink.MAX_PER_STUDENT,
    })


@login_required
def complete_profile(request):
    """Step 2: finish the personal profile, then land on the dashboard."""
    person = _person_for(request.user)
    if person is None:
        person = models.Person.objects.create(user=request.user)
    # Must register first.
    if not person.registered:
        return redirect('accounts:register')

    if request.method == 'POST':
        form = forms.CompleteProfileForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile_status = True
            obj.save()
            messages.success(request, 'Welcome aboard! Your profile is complete.')
            return redirect('myhub:index')
        messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
    else:
        form = forms.CompleteProfileForm(instance=person)
    return render(request, 'accounts/complete-profile.html', {
        'page_title': 'Complete your profile', 'form': form, 'person': person,
    })


# ---------------------------------------------------------------------------
# Profile — one page (templates/profiles/shell.html) for every person, course
# and module. The context is assembled in :mod:`core.profiles`.
# ---------------------------------------------------------------------------
@login_required
def my_profile(request):
    """My own profile — rendered through the shared profile shell."""
    person = _person_for(request.user)
    if person is None:
        return redirect('myhub:index')
    return _render_person_profile(request, person, 'feed')


@login_required
def profile(request, pk, tab='feed'):
    """Anyone's profile — the single person-profile page for the whole hub.

    The owner's ``UserSettings.profile_visibility`` gates access here (it has to
    redirect); the finer-grained filtering (contact details, grades, activity,
    Message vs Edit action) happens in :func:`core.profiles.person_context`.
    """
    person = get_object_or_404(models.Person.objects.select_related('user'), pk=pk)
    is_self = person.user_id == request.user.id
    viewer = _person_for(request.user)
    is_staff = (request.user.is_staff or request.user.is_superuser
                or (viewer and viewer.user_type in ('admin', 'staff')))

    if not is_self and not is_staff and person.user_id:
        vis = models.UserSettings.for_user(person.user).profile_visibility
        if vis == models.UserSettings.VISIBILITY_PRIVATE:
            messages.info(request, 'That member keeps their profile private.')
            return redirect('myhub:index')
        if vis == models.UserSettings.VISIBILITY_MEMBERS and not _shares_group(viewer, person):
            messages.info(request, 'That profile is only visible to members of the same course.')
            return redirect('myhub:index')

    return _render_person_profile(request, person, tab)


def _render_person_profile(request, person, tab):
    from core.profiles import PERSON_TABS, person_context, shell_base

    if tab not in {k for k, _l, _i in PERSON_TABS}:
        tab = 'feed'
    ctx = person_context(request, person, tab)
    ctx['page_title'] = str(person)
    ctx['base_template'] = shell_base(request)  # HTMX: tab swap → fragment only
    return render(request, 'accounts/my-profile.html', ctx)


def _shares_group(viewer_person, person):
    """True if the viewer and the profile owner share a course or a module.

    "Share a module" counts a module someone *teaches* as well as one they are
    *enrolled* in — otherwise an educator (who is never enrolled) could not open
    the profile of a student they teach, and vice-versa.
    """
    if not viewer_person:
        return False
    def module_ids(p):
        return set(p.selected_modules.values_list('pk', flat=True)) | \
               set(p.taught_modules.values_list('pk', flat=True))

    return bool(module_ids(viewer_person) & module_ids(person))


@login_required
def member_profile(request, pk):
    """Legacy alias — every person now renders on the one shared profile shell.

    Kept so old links (and the members directory) keep working; :func:`profile`
    owns the visibility gate and the tabs.
    """
    return redirect('accounts:profile', pk=pk)


def _email_verified(user):
    """True/False if allauth tracks a verified e-mail for ``user`` (None if
    allauth is unavailable)."""
    try:
        from allauth.account.models import EmailAddress
        return EmailAddress.objects.filter(user=user, verified=True).exists()
    except Exception:
        return None


@login_required
def settings(request):
    """The community settings hub: a tabbed page whose sections all persist.

    A single POST endpoint dispatches on the hidden ``form_name`` so the profile
    form, the preferences/privacy form and the password-change form each submit
    independently without clobbering the others.
    """
    person = _person_for(request.user)
    if person is None:
        person = models.Person.objects.create(user=request.user)
    user_settings = models.UserSettings.for_user(request.user)

    consent = _get_or_create_consent(person)
    study_profile, _ = models.PersonStudyProfile.objects.get_or_create(person=person)

    # Default (unbound) forms; the submitted one is re-bound below.
    profile_form = forms.ProfileForm(instance=person)
    settings_form = forms.UserSettingsForm(instance=user_settings)
    consent_form = forms.PrivacyConsentForm(instance=consent)
    active_tab = 'account'

    if request.method == 'POST':
        which = request.POST.get('form_name')
        if which == 'profile':
            active_tab = 'account'
            profile_form = forms.ProfileForm(request.POST, request.FILES, instance=person)
            if profile_form.is_valid():
                obj = profile_form.save(commit=False)
                obj.profile_status = True
                obj.save()
                messages.success(request, t('messages.saved', '{name} saved successfully.', name='Profile'))
                return redirect('accounts:my-profile')
            messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
        elif which == 'preferences':
            active_tab = 'preferences'
            settings_form = forms.UserSettingsForm(request.POST, instance=user_settings)
            if settings_form.is_valid():
                saved = settings_form.save()
                # Theme and language are chrome, not just stored rows: apply them
                # to THIS response immediately so the answer to "did it work?" is
                # the page the user lands on, not their next login. From the next
                # request on, UserPreferenceMiddleware reads them off the saved
                # row — the cookie below is only so the redirect itself is right.
                translation.activate(saved.language)
                messages.success(request, t('messages.saved', '{name} saved successfully.', name='Preferences'))
                response = redirect('accounts:settings')
                response.set_cookie(dj_settings.LANGUAGE_COOKIE_NAME, saved.language,
                                    max_age=365 * 24 * 3600, samesite='Lax')
                return response
            messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))
        elif which == 'calendar':
            active_tab = 'calendar'
            # No vacation dates: what we plan around is the institution's
            # assessment calendar, and a candidate's holidays are not ours to
            # keep.
            cats = {'exam': 'exam_dates', 'assignment': 'assignment_dates',
                    'practical': 'practical_dates'}
            for prefix, field in cats.items():
                labels = request.POST.getlist(f'{prefix}_label')
                dates = request.POST.getlist(f'{prefix}_date')
                rows = [{'label': (lbl or '').strip(), 'date': d}
                        for lbl, d in zip(labels, dates) if d]
                setattr(study_profile, field, rows)
            study_profile.save()
            messages.success(request, 'Your academic calendar has been saved.')
            return redirect('accounts:settings')
        elif which == 'consent':
            active_tab = 'consent'
            consent_form = forms.PrivacyConsentForm(request.POST, instance=consent)
            if consent_form.is_valid():
                obj = consent_form.save(commit=False)
                obj.consent_date = timezone.now()
                obj.consent_version = models.CONSENT_VERSION
                obj.consent_ip = _client_ip(request)
                obj.consent_device = request.META.get('HTTP_USER_AGENT', '')[:300]
                obj.save()
                messages.success(request, 'Your privacy choices have been saved.')
                return redirect('accounts:settings')
            messages.error(request, t('messages.form_errors', 'Please correct the errors highlighted below.'))

    # Connected calendars (the forms POST to apps.livesessions.views).
    from apps.livesessions.forms import CalendarSubscriptionForm
    from apps.livesessions.models import CalendarSubscription
    settings_row = models.UserSettings.for_user(request.user)

    if request.GET.get('tab') in ('connected',):
        active_tab = 'connected'

    return render(request, 'accounts/settings.html', {
        'page_title': 'Settings',
        'person': person,
        'calendar_subscriptions': CalendarSubscription.objects.filter(user=request.user),
        'calendar_form': CalendarSubscriptionForm(user=request.user),
        'calendar_feed_url': request.build_absolute_uri(
            reverse('livesessions:personal-feed', args=[settings_row.calendar_token])),
        'form': profile_form,               # kept for backwards-compat / clarity
        'profile_form': profile_form,
        'settings_form': settings_form,
        'consent_form': consent_form,
        'consent': consent,
        'consent_version': models.CONSENT_VERSION,
        'calendar_cats': [
            {'prefix': 'exam', 'title': 'Exam dates', 'icon': 'bi-mortarboard', 'rows': study_profile.exam_dates or []},
            {'prefix': 'assignment', 'title': 'Assignment dates', 'icon': 'bi-file-earmark-text', 'rows': study_profile.assignment_dates or []},
            {'prefix': 'practical', 'title': 'Practical dates', 'icon': 'bi-tools', 'rows': study_profile.practical_dates or []},
        ],
        'user_settings': user_settings,
        'email_verified': _email_verified(request.user),
        'active_tab': active_tab,
    })


# ---------------------------------------------------------------------------
# POPIA data-module rights + cookie consent
# ---------------------------------------------------------------------------
@login_required
@require_POST
def data_export(request):
    """POPIA right of access — download everything we hold about you as JSON,
    and record that an export was requested."""
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    consent = _get_or_create_consent(person)
    consent.data_export_requested = timezone.now()
    consent.save(update_fields=['data_export_requested', 'updated_at'])
    resp = JsonResponse(_serialize_person(person), json_dumps_params={'indent': 2})
    resp['Content-Disposition'] = f'attachment; filename="my-data-{request.user.pk}.json"'
    return resp


def _html_to_pdf(html):
    """Render an HTML string to PDF bytes (xhtml2pdf), or None on failure."""
    import io
    try:
        from xhtml2pdf import pisa
        buf = io.BytesIO()
        result = pisa.CreatePDF(html, dest=buf)
        return None if result.err else buf.getvalue()
    except Exception:  # pragma: no cover
        return None


def _export_sections(person):
    """Turn the raw data snapshot into humanised (title, [(label, value)]) sections."""
    raw = _serialize_person(person)
    titles = [
        ('account', 'Account'), ('profile', 'Profile'), ('contact', 'Contact & address'),
        ('study_profile', 'Academic calendar'), ('consent', 'Consent'),
    ]
    sections = []
    for key, title in titles:
        data = raw.get(key)
        if not data:
            continue
        rows = []
        for k, v in data.items():
            if v in (None, '', [], {}):
                continue
            if isinstance(v, list):
                v = ', '.join(str(x) for x in v)
            elif isinstance(v, dict):
                v = ', '.join(f'{a}: {b}' for a, b in v.items())
            rows.append((k.replace('_', ' ').capitalize(), v))
        if rows:
            sections.append((title, rows))
    return sections


@login_required
@require_POST
def data_export_pdf(request):
    """POPIA right of access — a human-readable PDF of the data we hold."""
    from core.branding import strings
    person = _person_for(request.user) or models.Person.objects.create(user=request.user)
    consent = _get_or_create_consent(person)
    consent.data_export_requested = timezone.now()
    consent.save(update_fields=['data_export_requested', 'updated_at'])
    html = render_to_string('accounts/data_export_pdf.html', {
        'sections': _export_sections(person), 'person': person,
        'brand': strings().get('brand', {}), 'now': timezone.now(),
    })
    pdf = _html_to_pdf(html)
    if pdf is None:                                   # fall back to JSON if PDF fails
        return data_export(request)
    resp = HttpResponse(pdf, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="my-data-{request.user.pk}.pdf"'
    return resp


@require_POST
def cookie_consent(request):
    """Record the cookie-banner choice: a year-long cookie for the browser, and
    (for signed-in users) the ``cookie_consent`` flag on their profile. Open to
    anonymous visitors so the banner works on public pages too."""
    accepted = request.POST.get('choice') == 'accept'
    if request.user.is_authenticated:
        person = _person_for(request.user)
        if person is not None:
            c = _get_or_create_consent(person)
            c.cookie_consent = accepted
            c.consent_date = timezone.now()
            c.consent_ip = _client_ip(request)
            c.save(update_fields=['cookie_consent', 'consent_date', 'consent_ip', 'updated_at'])
    resp = redirect(request.META.get('HTTP_REFERER') or '/')
    resp.set_cookie('cookie_consent', 'accepted' if accepted else 'declined',
                    max_age=60 * 60 * 24 * 365, samesite='Lax')
    return resp


# ---------------------------------------------------------------------------
# UI preferences set from the chrome (navbar theme buttons, language switcher)
# ---------------------------------------------------------------------------
@login_required
@require_POST
def set_theme(request):
    """Persist the light/dark/auto choice made from the navbar.

    The navbar toggle and the Theme field on the settings page are the same
    setting, so both write the same row — flipping it in the navbar is
    remembered on the next sign-in and on the user's other devices, which is
    what "the system is in dark mode" has to mean.
    """
    theme = (request.POST.get('theme') or '').strip()
    valid = {value for value, _label in models.UserSettings.THEME_CHOICES}
    if theme not in valid:
        return JsonResponse({'ok': False, 'error': 'unknown theme'}, status=400)
    user_settings = models.UserSettings.for_user(request.user)
    user_settings.theme = theme
    user_settings.save(update_fields=['theme', 'updated_at'])
    response = JsonResponse({'ok': True, 'theme': theme})
    response.set_cookie('ui_theme', theme, max_age=365 * 24 * 3600, samesite='Lax')
    return response


@login_required
def set_language(request):
    """Switch interface language and return where the user came from.

    ``UserPreferenceMiddleware`` reads the saved row on every later request, so
    this only has to write it and bounce back.
    """
    language = (request.GET.get('lang') or request.POST.get('lang') or '').strip()
    valid = {code for code, _label in dj_settings.LANGUAGES}
    if language in valid:
        user_settings = models.UserSettings.for_user(request.user)
        user_settings.language = language
        user_settings.save(update_fields=['language', 'updated_at'])
        translation.activate(language)
    response = redirect(request.META.get('HTTP_REFERER') or 'myhub:index')
    if language in valid:
        response.set_cookie(dj_settings.LANGUAGE_COOKIE_NAME, language,
                            max_age=365 * 24 * 3600, samesite='Lax')
    return response


# ---------------------------------------------------------------------------
# Close account (verify → soft close → 30-day grace → purge command)
# ---------------------------------------------------------------------------
@login_required
def close_account(request):
    """Verify the user, then soft-close their account (30-day grace)."""
    user_settings = models.UserSettings.for_user(request.user)

    if request.method == 'POST':
        form = forms.CloseAccountForm(request.user, request.POST)
        if form.is_valid():
            user_settings.mark_closing()
            request.user.is_active = False
            request.user.save(update_fields=['is_active'])
            logout(request)
            # Render the confirmation in THIS (already-authenticated) response so
            # the now-anonymous user isn't bounced to the login page by the
            # site-wide LoginRequiredMiddleware.
            return render(request, 'accounts/close-account-done.html', {
                'page_title': 'Account closed',
                'grace_days': models.UserSettings.GRACE_DAYS,
            })
        messages.error(request, 'Could not close your account — see the errors below.')
    else:
        form = forms.CloseAccountForm(request.user)

    return render(request, 'accounts/close-account.html', {
        'page_title': 'Close account', 'form': form,
        'grace_days': models.UserSettings.GRACE_DAYS,
    })


@login_required
def close_account_done(request):
    """Standalone post-closure confirmation page (also shown inline on POST)."""
    return render(request, 'accounts/close-account-done.html', {
        'page_title': 'Account closed',
        'grace_days': models.UserSettings.GRACE_DAYS,
    })


# ---------------------------------------------------------------------------
# Admin / staff: manage anyone's course + module enrolment
# ---------------------------------------------------------------------------
@login_required
def manage_members(request):
    """Admin/staff roster: every person with the modules they are enrolled in."""
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to manage members.')
        return redirect('myhub:index')
    people = (models.Person.objects.select_related('user')
              .order_by('first_name', 'last_name'))
    # Registered, but holding no open module: they have an enrolment row and a
    # settled (or absent) registration invoice, and every module is still locked.
    from apps.learning.models import ModuleEnrolment
    open_states = [ModuleEnrolment.STATUS_TRIAL, ModuleEnrolment.STATUS_ACTIVE]
    pending = (models.Person.objects
               .filter(registered=True, pending_invoice_uid__isnull=True,
                       module_enrolments__isnull=False)
               .exclude(module_enrolments__status__in=open_states)
               .select_related('user')
               .distinct()
               .order_by('first_name', 'last_name'))
    return render(request, 'accounts/manage-members.html', {
        'page_title': 'Manage members', 'people': people, 'pending': pending,
    })


@login_required
@require_POST
def member_role(request, pk):
    """Change what kind of account someone has. **Administrators only.**

    Every account is created as a student — self sign-up has no role picker, and
    the invite links carry their own role. Becoming an educator or a staff member
    is therefore something that is *granted*, not claimed, and only an
    administrator can grant it: staff can enrol and manage students, but letting
    them mint more staff would make the distinction meaningless.

    Demoting the last administrator is refused, because an installation with
    nobody who can grant roles cannot be recovered from inside the app.
    """
    role = role_flags(request).get('user_role')
    is_admin = role == 'admin' or request.user.is_superuser
    if not is_admin:
        note('USER-2001', request, kind='role-change')
        messages.error(request, 'Only an administrator can change what kind of account '
                                'someone has.')
        return redirect('accounts:manage-members')

    person = get_object_or_404(models.Person.objects.select_related('user'), pk=pk)
    new_role = (request.POST.get('user_type') or '').strip()
    allowed = {'student', 'educator', 'staff', 'admin', 'parent'}
    if new_role not in allowed:
        messages.error(request, 'That is not a role this platform recognises.')
        return redirect('accounts:manage-members')

    if person.user_type == 'admin' and new_role != 'admin':
        remaining = (models.Person.objects.filter(user_type='admin')
                     .exclude(pk=person.pk).exists())
        if not remaining:
            messages.error(request, 'That is the only administrator left — promote somebody '
                                    'else first, or you will lock everyone out of managing '
                                    'this platform.')
            return redirect('accounts:manage-members')

    was = person.get_user_type_display()
    person.user_type = new_role
    person.save(update_fields=['user_type'])
    # Django-admin access follows the role: administrators get it, nobody else.
    user = person.user
    wants_django_admin = new_role == 'admin'
    if user.is_staff != wants_django_admin and not user.is_superuser:
        user.is_staff = wants_django_admin
        user.save(update_fields=['is_staff'])
    messages.success(request, f'{person} is now {person.get_user_type_display()} '
                              f'(was {was}).')
    return redirect('accounts:manage-members')


@login_required
def member_enrol(request, pk):
    """Admin/staff: put a person into a programme's module offerings.

    The picker lists programmes; ticking modules writes ``ModuleEnrolment``
    rows through :func:`apps.accounts.services.set_module_membership`. Added
    modules start locked — enrolment is not payment.
    """
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to manage members.')
        return redirect('myhub:index')

    from apps.learning.models import Programme, ProgrammeModule
    person = get_object_or_404(models.Person.objects.select_related('user'), pk=pk)
    held = set(person.selected_modules.values_list('id', flat=True))

    if request.method == 'POST':
        wanted = {int(i) for i in request.POST.getlist('modules') if str(i).isdigit()}
        services.set_module_membership(
            person, add_ids=wanted - held, remove_ids=held - wanted)
        messages.success(request, f'Enrolment updated for {person}.')
        return redirect('accounts:manage-members')

    programmes = (Programme.objects.filter(is_active=True)
                  .select_related('institution').order_by('institution__name', 'name'))
    modules = (ProgrammeModule.objects.filter(is_active=True)
               .select_related('programme', 'module')
               .order_by('programme__name', 'order', 'name'))
    return render(request, 'accounts/member-enrol.html', {
        'page_title': f'Enrol · {person}', 'person': person,
        'programmes': programmes, 'modules': modules,
        'enrolled_module_ids': held,
    })


# ---------------------------------------------------------------------------
# Admin / staff: closed accounts — reactivate during grace, restore after purge
# ---------------------------------------------------------------------------
@login_required
def closed_accounts(request):
    """The recovery desk for closed accounts.

    Two lists, because a closed account is in one of two very different states:

    * **In the grace period** — closed within the last
      :attr:`~apps.accounts.models.UserSettings.GRACE_DAYS` days. The account is
      merely deactivated; reactivating it is instant and complete.
    * **Archived** — the grace period elapsed and ``purge_closed_accounts``
      moved everything to the archive park. Restoring rebuilds the account from
      that directory; what it cannot rebuild are the links deliberately dropped
      so other people's threads stayed intact.
    """
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to manage closed accounts.')
        return redirect('myhub:index')

    now = timezone.now()
    closing = (models.UserSettings.objects
               .filter(is_closing=True)
               .select_related('user', 'user__profile')
               .order_by('purge_at'))
    rows = []
    for user_settings in closing:
        remaining = None
        if user_settings.purge_at:
            remaining = (user_settings.purge_at - now).days
        rows.append({'settings': user_settings, 'user': user_settings.user,
                     'person': getattr(user_settings.user, 'profile', None),
                     'days_left': remaining,
                     'overdue': remaining is not None and remaining < 0})

    archives = models.AccountArchive.objects.all()[:200]

    return render(request, 'accounts/closed-accounts.html', {
        'page_title': 'Closed accounts',
        'closing': rows,
        'archives': archives,
        'grace_days': models.UserSettings.GRACE_DAYS,
    })


@login_required
@require_POST
def reactivate_account(request, pk):
    """Undo a closure that is still inside its grace period."""
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to reactivate accounts.')
        return redirect('myhub:index')

    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    user_settings = models.UserSettings.for_user(user)
    if not user_settings.is_closing:
        messages.info(request, f'{user.email or user} is not a closed account.')
        return redirect('accounts:closed-accounts')

    user_settings.cancel_closing()
    user.is_active = True
    user.save(update_fields=['is_active'])
    messages.success(
        request,
        f'{user.email or user} has been reactivated. They can sign in again with '
        f'their existing password.')
    return redirect('accounts:closed-accounts')


@login_required
@require_POST
def restore_archive(request, pk):
    """Rebuild a purged account from the archive park."""
    if not _require_admin_staff(request):
        messages.error(request, 'You do not have permission to restore accounts.')
        return redirect('myhub:index')

    archive = get_object_or_404(models.AccountArchive, pk=pk)
    if archive.restored_at:
        messages.info(request, f'{archive.display_name} has already been restored.')
        return redirect('accounts:closed-accounts')

    from . import archiving
    try:
        user = archiving.restore_archive(archive)
    except Exception as exc:
        report('USER-2004', exc, request, context={'archive': archive.pk})
        messages.error(
            request,
            f'Could not restore {archive.display_name}: {exc}. The archive is '
            f'untouched — nothing was lost by the attempt.')
        return redirect('accounts:closed-accounts')

    messages.success(
        request,
        f'{archive.display_name} has been restored from the archive '
        f'({archive.content_rows} row(s)). Their password was not restored — ask '
        f'them to use “Forgot password” on the login page to set a new one.')
    return redirect('accounts:member-profile', pk=getattr(getattr(user, 'profile', None), 'pk', 0)) \
        if getattr(user, 'profile', None) else redirect('accounts:closed-accounts')
