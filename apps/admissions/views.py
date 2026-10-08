"""Admissions pages.

* ``my_application`` — the family's view of the application: status, the
  document checklist (upload what is still outstanding), the invoice.
* ``document_file`` — serves an uploaded document to the office, the learner's
  own account, or a linked parent. Never public.
* ``office_list`` / ``office_detail`` — the school office: every application
  with filters, and one application in full with the page-1 "office use only"
  checklist, document verification and the admission decision.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.roles import role_flags

from . import forms, services
from .models import Application, ApplicationDocument


def _is_office(request):
    return role_flags(request).get('is_admin_staff', False) or request.user.is_superuser


def _can_see(request, application):
    """Office, the learner, or a parent linked to the learner."""
    if _is_office(request):
        return True
    user = request.user
    if application.person.user_id == user.id:
        return True
    from core.scoping import children_of
    return children_of(user).filter(pk=application.person.user_id).exists()


def _family_applications(request):
    """The applications the signed-in learner / parent may see."""
    from core.scoping import children_of
    user = request.user
    child_ids = list(children_of(user).values_list('pk', flat=True))
    return (Application.objects
            .filter(Q(person__user=user) | Q(person__user_id__in=child_ids))
            .select_related('person__user', 'programme')
            .prefetch_related('documents', 'guardians'))


def _invoice_for(application):
    if not application.invoice_uid:
        return None
    from apps.finance.models import Invoice
    return Invoice.objects.filter(public_id=application.invoice_uid).first()


@login_required
def my_application(request):
    """Status, checklist and outstanding documents for the family."""
    applications = list(_family_applications(request))
    if not applications:
        person = getattr(request.user, 'profile', None)
        if person is not None and person.user_type == 'student':
            return redirect('accounts:register')
        messages.info(request, 'There is no application on this account yet.')
        return redirect('myhub:index')

    if request.method == 'POST':
        application = get_object_or_404(Application, pk=request.POST.get('application'))
        if not _can_see(request, application) or not application.is_open:
            raise Http404
        from apps.accounts.views import _save_uploaded_documents
        if not _save_uploaded_documents(request, application):
            services.refresh_status(application)
            messages.success(request, 'Thank you — the document has been added to the application.')
        return redirect('admissions:my-application')

    labels = dict(ApplicationDocument.KIND_CHOICES)
    cards = []
    for application in applications:
        held = {}
        for doc in application.documents.all():
            held.setdefault(doc.kind, []).append(doc)
        required = application.required_document_kinds()
        cards.append({
            'application': application,
            'invoice': _invoice_for(application),
            'checklist': [{'kind': kind, 'label': labels[kind], 'held': held.get(kind, [])}
                          for kind in required],
            'extra': [doc for kind, docs in held.items() if kind not in required for doc in docs],
            'missing': application.missing_documents(),
        })
    return render(request, 'admissions/my-application.html', {
        'page_title': 'My application', 'cards': cards,
        'upload_kinds': ApplicationDocument.KIND_CHOICES,
    })


@login_required
def document_file(request, pk):
    document = get_object_or_404(ApplicationDocument.objects.select_related('application__person'),
                                 pk=pk)
    if not _can_see(request, document.application) or not document.file:
        raise Http404
    return FileResponse(document.file.open('rb'), as_attachment=False,
                        filename=document.original_name or document.file.name.rsplit('/', 1)[-1])


# ---------------------------------------------------------------------------
# The school office
# ---------------------------------------------------------------------------
@login_required
def office_list(request):
    if not _is_office(request):
        raise Http404
    qs = (Application.objects.select_related('person__user', 'programme')
          .annotate(document_count=Count('documents')))
    status = request.GET.get('status') or ''
    grade = request.GET.get('grade') or ''
    q = (request.GET.get('q') or '').strip()
    if status in dict(Application.STATUS_CHOICES):
        qs = qs.filter(status=status)
    elif not status:
        qs = qs.exclude(status=Application.STATUS_DRAFT)
    if grade.isdigit():
        qs = qs.filter(programme__grade=int(grade))
    if q:
        qs = qs.filter(Q(person__first_name__icontains=q) | Q(person__last_name__icontains=q)
                       | Q(person__user__email__icontains=q) | Q(id_number__icontains=q)
                       | Q(guardians__full_name__icontains=q)
                       | Q(office_account_number__icontains=q)).distinct()
    counts = dict(Application.objects.values_list('status').annotate(n=Count('id')))
    return render(request, 'admissions/office-list.html', {
        'page_title': 'Admissions', 'applications': qs[:300],
        'status_rows': [(value, label.split(' — ')[0], counts.get(value, 0))
                        for value, label in Application.STATUS_CHOICES],
        'filters': {'status': status, 'grade': grade, 'q': q}, 'grades': range(1, 13),
    })


@login_required
def office_detail(request, public_id):
    if not _is_office(request):
        raise Http404
    application = get_object_or_404(
        Application.objects.select_related('person__user', 'person__contact', 'programme'),
        public_id=public_id)
    form = forms.OfficeChecklistForm(request.POST or None, instance=application, prefix='office')

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        if action == 'verify':
            doc = get_object_or_404(ApplicationDocument, pk=request.POST.get('document'),
                                    application=application)
            doc.verified = not doc.verified
            doc.verified_by = request.user if doc.verified else None
            doc.verified_at = timezone.now() if doc.verified else None
            doc.save(update_fields=['verified', 'verified_by', 'verified_at', 'updated_at'])
            return redirect('admissions:office-detail', public_id=application.public_id)
        if action == 'invite':
            sent = services.invite_guardians(application, invited_by=request.user)
            messages.success(request, f'Parent invitations sent to {", ".join(sent)}.' if sent
                             else 'No new parent invitations to send.')
            return redirect('admissions:office-detail', public_id=application.public_id)
        if action in ('admit', 'decline'):
            status = (Application.STATUS_ADMITTED if action == 'admit'
                      else Application.STATUS_DECLINED)
            services.decide(application, request.user, status,
                            note=request.POST.get('decision_note', '').strip())
            messages.success(request, f'{application.learner_name}: {application.get_status_display()}.')
            return redirect('admissions:office-detail', public_id=application.public_id)
        if form.is_valid():
            application = form.save(commit=False)
            if request.POST.get('sign_registrar') and not application.registrar_id:
                application.registrar = request.user
                application.registrar_signed_at = timezone.now()
            application.save()
            messages.success(request, 'Application updated.')
            return redirect('admissions:office-detail', public_id=application.public_id)

    labels = dict(ApplicationDocument.KIND_CHOICES)
    held = {}
    for doc in application.documents.all():
        held.setdefault(doc.kind, []).append(doc)
    required = application.required_document_kinds()
    return render(request, 'admissions/office-detail.html', {
        'page_title': f'Application — {application.learner_name}',
        'application': application, 'form': form,
        'guardians': application.guardians.all(),
        'checklist': [{'kind': kind, 'label': labels[kind], 'held': held.get(kind, [])}
                      for kind in required],
        'extra': [doc for kind, docs in held.items() if kind not in required for doc in docs],
        'invoice': _invoice_for(application),
        'enrolled_subjects': application.person.module_enrolments.select_related(
            'programme_module__module').filter(programme_module__programme=application.programme_id)
        if application.programme_id else [],
    })
