"""Developer/admin pages: the error dictionary and the error log.

Both are **restricted to admins and staff**. The log carries tracebacks, request
paths and user identities — it is a map of how to break the platform, so it is
gated on the same check the rest of the management area uses, and educators,
parents and learners never see it.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.roles import role_flags

from . import catalog
from .models import ErrorEvent

logger = logging.getLogger('apps.diagnostics')


def _require_developer(request):
    """Admins and staff only. Raises 404 for anyone else.

    404 rather than 403 on purpose: there is no reason to advertise that an
    error console exists to someone who may not use it.
    """
    if not role_flags(request)['is_admin_staff']:
        raise Http404
    return True


# ---------------------------------------------------------------------------
# The dictionary
# ---------------------------------------------------------------------------
@login_required
def dictionary(request):
    """Every documented error code, grouped by domain."""
    _require_developer(request)

    query = (request.GET.get('q') or '').strip().lower()
    domain = (request.GET.get('domain') or '').strip().upper()

    specs = sorted(catalog.ERRORS.values(), key=lambda s: s.code)
    if domain in catalog.PREFIXES:
        specs = [s for s in specs if catalog.prefix_of(s.code) == domain]
    if query:
        specs = [s for s in specs
                 if query in s.code.lower() or query in s.title.lower()
                 or query in s.why.lower() or query in s.fix.lower()]

    # How often each code has actually fired, so the dictionary doubles as a
    # heat map rather than a static reference nobody revisits.
    counts = {row['code']: row['total'] for row in
              ErrorEvent.objects.values('code').annotate(total=Sum('count'))}

    grouped = {}
    for spec in specs:
        grouped.setdefault(catalog.prefix_of(spec.code), []).append({
            'spec': spec,
            'cause': catalog.cause_label(spec.code),
            'seen': counts.get(spec.code, 0),
        })

    return render(request, 'diagnostics/dictionary.html', {
        'page_title': 'Error dictionary',
        'grouped': sorted(grouped.items()),
        'domains': sorted(catalog.PREFIXES.items()),
        'causes': sorted(catalog.CAUSE_CLASSES.items()),
        'query': request.GET.get('q', ''),
        'active_domain': domain,
        'total_codes': len(catalog.ERRORS),
        'problems': catalog.validate(),
    })


# ---------------------------------------------------------------------------
# The log
# ---------------------------------------------------------------------------
@login_required
def log(request):
    """The error log, newest first, with filters and a triage summary."""
    _require_developer(request)

    events = ErrorEvent.objects.select_related('user')

    status = (request.GET.get('status') or 'open').strip()
    severity = (request.GET.get('severity') or '').strip()
    domain = (request.GET.get('domain') or '').strip().upper()
    query = (request.GET.get('q') or '').strip()

    if status == 'open':
        events = events.filter(status__in=[ErrorEvent.STATUS_OPEN, ErrorEvent.STATUS_ACKNOWLEDGED])
    elif status in dict(ErrorEvent.STATUS_CHOICES):
        events = events.filter(status=status)
    if severity in catalog.SEVERITIES:
        events = events.filter(severity=severity)
    if domain in catalog.PREFIXES:
        events = events.filter(code__startswith=f'{domain}-')
    if query:
        events = events.filter(
            Q(code__icontains=query) | Q(message__icontains=query)
            | Q(module__icontains=query) | Q(path__icontains=query)
            | Q(reference__iexact=query) | Q(exception_type__icontains=query))

    summary = {
        'open': ErrorEvent.objects.filter(
            status__in=[ErrorEvent.STATUS_OPEN, ErrorEvent.STATUS_ACKNOWLEDGED]).count(),
        'critical': ErrorEvent.objects.filter(
            severity='critical', status=ErrorEvent.STATUS_OPEN).count(),
        'occurrences': ErrorEvent.objects.aggregate(n=Sum('count'))['n'] or 0,
        'undocumented': sum(1 for e in ErrorEvent.objects.only('code')
                            if e.code not in catalog.ERRORS),
    }
    top = (ErrorEvent.objects.values('code')
           .annotate(total=Sum('count'), rows=Count('id'))
           .order_by('-total')[:8])

    return render(request, 'diagnostics/log.html', {
        'page_title': 'Error log',
        'events': events[:300],
        'summary': summary,
        'top': [dict(row, spec=catalog.get(row['code'])) for row in top],
        'statuses': ErrorEvent.STATUS_CHOICES,
        'severities': catalog.SEVERITIES,
        'domains': sorted(catalog.PREFIXES.items()),
        'active': {'status': status, 'severity': severity, 'domain': domain, 'q': query},
    })


@login_required
def event_detail(request, pk):
    """One error in full: traceback, context, and what the catalog says to do."""
    _require_developer(request)
    event = get_object_or_404(ErrorEvent.objects.select_related('user', 'resolved_by'), pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        note = (request.POST.get('note') or '').strip()
        if action == 'resolve':
            event.resolve(user=request.user, note=note)
            messages.success(request, f'{event.code} marked resolved.')
        elif action in ('ack', 'ignored', 'open'):
            event.status = {'ack': ErrorEvent.STATUS_ACKNOWLEDGED,
                            'ignored': ErrorEvent.STATUS_IGNORED,
                            'open': ErrorEvent.STATUS_OPEN}[action]
            if note:
                event.note = note
            event.save(update_fields=['status', 'note'])
            messages.success(request, f'{event.code} marked {event.get_status_display().lower()}.')
        elif action == 'note':
            event.note = note
            event.save(update_fields=['note'])
            messages.success(request, 'Note saved.')
        return redirect('diagnostics:event', pk=event.pk)

    # Other recent errors from the same module — a fault rarely arrives alone.
    related = (ErrorEvent.objects.filter(module=event.module)
               .exclude(pk=event.pk).order_by('-last_seen')[:8]) if event.module else []

    return render(request, 'diagnostics/event.html', {
        'page_title': f'{event.code} · error detail',
        'event': event,
        'spec': event.spec,
        'cause': event.cause,
        'related': related,
    })


@login_required
def export_log(request):
    """The current filter's results as CSV, for triage outside the browser."""
    _require_developer(request)
    import csv

    response = HttpResponse(content_type='text/csv')
    stamp = timezone.now().strftime('%Y%m%d-%H%M')
    response['Content-Disposition'] = f'attachment; filename="error-log-{stamp}.csv"'

    writer = csv.writer(response)
    writer.writerow(['code', 'title', 'severity', 'cause', 'status', 'count',
                     'first_seen', 'last_seen', 'module', 'function', 'line',
                     'exception', 'path', 'user', 'reference', 'message'])
    for event in ErrorEvent.objects.select_related('user')[:5000]:
        writer.writerow([
            event.code, event.title, event.severity, event.cause, event.status,
            event.count, event.first_seen.isoformat(), event.last_seen.isoformat(),
            event.module, event.function, event.line or '', event.exception_type,
            event.path, event.user_label, event.reference,
            (event.message or '').replace('\n', ' ')[:500],
        ])
    return response


@login_required
def dictionary_json(request):
    """The whole catalog as JSON, so tooling and support scripts can read it."""
    _require_developer(request)
    return JsonResponse({
        'causes': {str(k): {'name': v[0], 'meaning': v[1]}
                   for k, v in catalog.CAUSE_CLASSES.items()},
        'domains': catalog.PREFIXES,
        'errors': {spec.code: {
            'title': spec.title, 'why': spec.why, 'fix': spec.fix,
            'action': spec.action, 'severity': spec.severity,
            'domain': catalog.prefix_of(spec.code),
            'cause': catalog.cause_label(spec.code),
        } for spec in catalog.ERRORS.values()},
    }, json_dumps_params={'indent': 2})
