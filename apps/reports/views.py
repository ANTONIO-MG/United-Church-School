"""HTML views for reports & certificates.

Who sees what:

* **student**          — their own grades and their own certificates.
* **parent**           — the grades and certificates of the child(ren) they are
  linked to, and nobody else's. A parent following their child's progress is the
  whole point of the account, so they see the results but never the class around
  them.
* **educator**         — grades for the modules they teach, and **no certificates
  at all**. A learner's certificate is theirs and the institution's; an educator
  marks the work but has no business browsing the awards. Every certificate route
  therefore 404s for an educator (see :func:`_certificate_for`) and the page hides
  the section entirely.
* **admin / staff**    — everything.

Grades stay visible to educators because marking depends on them — only the
certificate half is withheld.
"""

import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.roles import role_flags
from core.scoping import children_of, taught_module_qs

from . import certificates, models, services

logger = logging.getLogger('apps')


@login_required
def my_reports(request):
    flags = role_flags(request)
    grades = models.Grade.objects.select_related('student', 'module')
    certs = models.Certificate.objects.select_related('student', 'module')

    children = None
    if flags['is_admin_staff']:
        pass                                    # the institution's whole gradebook
    elif flags['is_educator']:
        # Marking needs grades — but only for the modules actually taught, and
        # never any certificate.
        grades = grades.filter(module__in=taught_module_qs(request.user))
        certs = certs.none()
    elif flags['is_parent']:
        # A parent's report card is their child's. Never their own (they sit no
        # assessments) and never anyone else's.
        children = children_of(request.user)
        grades = grades.filter(student__in=children)
        certs = certs.filter(student__in=children)
    else:
        grades = grades.filter(student=request.user)
        certs = certs.filter(student=request.user)

    return render(request, 'reports/my-reports.html', {
        'page_title': 'Reports' if flags['is_educator'] else 'Reports & Certificates',
        'grades': grades.order_by('module', '-final_pct')[:200],
        'certificates': certs.order_by('-issued_at')[:200],
        'show_certificates': not flags['is_educator'],
        'children': children,
    })


def _certificate_for(request, pk):
    """The certificate, if this user is allowed to see it.

    A student may see their own, a parent their child's, and admin/staff any.
    **Educators may see none** — not their students' and not their own; the whole
    surface is closed to them. Everyone else gets a 404 rather than a 403, so a
    certificate someone can't see is never even confirmed to exist.
    """
    cert = get_object_or_404(
        models.Certificate.objects.select_related('student', 'module'), pk=pk)
    flags = role_flags(request)
    if flags['is_admin_staff']:
        allowed = True
    elif flags['is_educator']:
        allowed = False
    elif flags['is_parent']:
        allowed = children_of(request.user).filter(pk=cert.student_id).exists()
    else:
        allowed = cert.student_id == request.user.id
    if not allowed:
        from django.http import Http404
        raise Http404
    return cert


@login_required
def certificate_view(request, pk):
    """On-screen preview — the same artwork the PNG and PDF are cut from."""
    cert = _certificate_for(request, pk)
    try:
        ctx = certificates.certificate_context(cert, request)
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
        return redirect('reports:my-reports')
    ctx['page_title'] = cert.title
    return render(request, 'reports/certificate.html', ctx)


def _certificate_download(request, pk, *, renderer, content_type, extension, disposition):
    """Shared plumbing for the image/PDF endpoints.

    ``disposition`` is ``attachment`` for a download and ``inline`` for the copy
    the preview page embeds, so the same rendering path serves both.
    """
    cert = _certificate_for(request, pk)
    try:
        data = renderer(cert, request)
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
        return redirect('reports:my-reports')
    except Exception:
        logger.exception('reports: certificate %s failed to render', cert.pk)
        messages.error(request, 'That certificate could not be rendered just now.')
        return redirect('reports:my-reports')

    response = HttpResponse(data, content_type=content_type)
    response['Content-Disposition'] = f'{disposition}; filename="{cert.number}.{extension}"'
    response['Content-Length'] = str(len(data))
    return response


@login_required
def certificate_pdf(request, pk):
    """Download the certificate as a print-ready A4-landscape PDF."""
    return _certificate_download(
        request, pk, renderer=certificates.ensure_pdf,
        content_type='application/pdf', extension='pdf', disposition='attachment')


@login_required
def certificate_png(request, pk):
    """Download the certificate as a PNG image."""
    return _certificate_download(
        request, pk, renderer=lambda c, r: certificates.render_png(c, r, scale=1.5),
        content_type='image/png', extension='png', disposition='attachment')


@login_required
def certificate_image(request, pk):
    """The same PNG, served inline — this is what the preview page displays."""
    return _certificate_download(
        request, pk, renderer=lambda c, r: certificates.render_png(c, r, scale=1.0),
        content_type='image/png', extension='png', disposition='inline')


@login_required
def my_progress(request):
    """Unified progress dashboard: a student's grades, tasks, assessments, study
    time and attendance with charts.

    This *is* the analytics page for a single learner, so each role reaches it
    through the same view with a different pool of students behind ``?student=``:
    staff see any, an educator the students they teach, and a parent only their
    own child(ren). Selecting is always done with ``get_object_or_404`` against
    that pool, so an id from outside it is a 404 rather than someone else's data.
    """
    flags = role_flags(request)
    target = request.user
    students = None
    if flags['is_admin_staff'] or flags['is_educator'] or flags['is_parent']:
        User = get_user_model()
        if flags['is_parent']:
            students = children_of(request.user)
        else:
            students = User.objects.filter(profile__user_type='student')
            if not flags['is_admin_staff']:
                students = students.filter(
                    profile__module_enrolments__programme_module__in=taught_module_qs(request.user))
        students = students.distinct().order_by('first_name', 'last_name', 'username')
        sid = request.GET.get('student')
        if sid:
            target = get_object_or_404(students, pk=sid)
        elif flags['is_parent']:
            # A parent has no progress of their own — open on their child.
            target = students.first() or request.user

    progress = services.student_progress(target)
    # Pre-serialise the bits the charts need so the template stays clean.
    chart = {
        'subject_labels': [s['name'] for s in progress['modules']],
        'subject_scores': [s['final_pct'] for s in progress['modules']],
        'task_status_labels': list((progress['tasks'].get('by_status') or {}).keys()),
        'task_status_counts': list((progress['tasks'].get('by_status') or {}).values()),
    }
    name = target.get_full_name() or target.get_username()
    return render(request, 'reports/my-progress.html', {
        'page_title': 'My Progress' if target == request.user else f'Progress · {name}',
        'progress': progress,
        'chart_json': json.dumps(chart),
        'target': target,
        'students': students,
        'is_own': target == request.user,
        # The picker reads as "whose progress am I looking at" for a parent, and
        # as "pick a student" for staff.
        'picker_label': 'Child' if flags['is_parent'] else 'Student',
    })


def verify_certificate(request, verification_uuid):
    """Public certificate verification by UUID. A revoked certificate is still
    found — and reported as revoked, which is the answer a verifier needs."""
    cert = get_object_or_404(models.Certificate, verification_uuid=verification_uuid)
    return render(request, 'reports/verify.html', {
        'page_title': 'Certificate verification', 'cert': cert,
        'valid': not cert.is_revoked, 'revoked': cert.is_revoked,
    })
