"""Ops pages: background jobs, moderation, audit log, invitations and parent links.

Each of these used to mean Django admin or a shell. The pages call the same
service functions the rest of the app uses, so a decision taken here follows
the same rules as one taken anywhere else.
"""

import csv
import threading
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import connections
from django.db.models import Count, Q
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounts import emails as account_emails
from apps.accounts.models import ActivityLog, Invitation, ParentLink
from apps.communication import services as comms
from apps.communication.models import Appeal, Penalty, ReputationScore, Violation
from apps.scheduler import jobs as job_registry
from apps.scheduler import runner
from apps.scheduler.models import JobRun
from core.utils import display_name

from .access import staff_required
from .forms_ops import AppealDecisionForm, AuditFilterForm, ParentLinkForm

PAGE_SIZE = 50


def _page(request, qs, size=PAGE_SIZE):
    """A page of ``qs`` plus the current query string minus ``page``, for links."""
    page = Paginator(qs, size).get_page(request.GET.get('page'))
    keep = request.GET.copy()
    keep.pop('page', None)
    return page, keep.urlencode()


def _user_q(prefix, term):
    """Match a user (via ``prefix``) by e-mail or either copy of their name."""
    q = Q()
    for field in ('email', 'first_name', 'last_name', 'profile__first_name', 'profile__last_name'):
        q |= Q(**{f'{prefix}{field}__icontains': term})
    return q


def _back(request, fallback):
    """Return to the page the form was on (keeping its tab and filters)."""
    nxt = request.POST.get('next', '')
    return redirect(nxt if nxt.startswith('/') and not nxt.startswith('//') else fallback)


# ===========================================================================
# Background jobs
# ===========================================================================
SAST = ZoneInfo('Africa/Johannesburg')

#: The jobs the quarter-hourly timer runs (deploy/scheduler/production/*-quick.service).
QUICK_JOBS = ('session-reminders', 'send-broadcasts', 'shop-bookings', 'auto-notices')

#: How late past its expected tick a job may start before it is called overdue.
#: The main tick runs jobs one after another, so a slow job delays the rest.
OVERDUE_SLACK = timedelta(minutes=30)

SCHEDULE_TEXT = [
    ('Main tick', 'Hourly at :05 from 06:05 to 22:05 SAST — runs every job that is due.'),
    ('Quick tick', 'Every 15 minutes from 06:00 to 22:45 SAST — runs ' + ', '.join(QUICK_JOBS) + '.'),
    ('Overnight', 'Nothing runs between 22:45 and 06:00; work that fell due overnight runs on the first morning tick.'),
]


def _ticks_on(day, quick):
    """Production tick times (aware, SAST) on ``day`` for a main or quick job."""
    slots = {time(h, 5) for h in range(6, 23)}
    if quick:
        slots |= {time(h, m) for h in range(6, 23) for m in (0, 15, 30, 45)}
    return sorted(datetime.combine(day, t, tzinfo=SAST) for t in slots)


def next_expected_run(job, state, now):
    """When the production timers should next start ``job``.

    Mirrors :func:`apps.scheduler.runner.is_due`: the job becomes due a little
    before its full interval, then waits for the next tick that includes it.
    """
    if state is None or state.last_started_at is None:
        due = now
    else:
        grace = min(runner.GRACE_SECONDS, job.every * 0.1)
        due = state.last_started_at + timedelta(seconds=job.every - grace)
    start = due.astimezone(SAST).date()
    for offset in range(3):
        for tick in _ticks_on(start + timedelta(days=offset), job.name in QUICK_JOBS):
            if tick >= due:
                return tick
    return None


def _is_locked(state, now):
    return bool(state and state.locked_at
                and (now - state.locked_at).total_seconds() < job_registry.LOCK_STALE_AFTER)


def _every_label(seconds):
    if seconds % 3600 == 0:
        h = seconds // 3600
        return 'hourly' if h == 1 else f'every {h} h'
    m = seconds // 60
    return 'every minute' if m == 1 else f'every {m} min'


def _duration_label(ms):
    if ms < 1000:
        return f'{ms} ms'
    if ms < 60_000:
        return f'{ms / 1000:.1f} s'
    return f'{ms / 60_000:.1f} min'


def _job_rows(now):
    states = {s.name: s for s in JobRun.objects.all()}
    rows = []
    for job in job_registry.JOBS:
        state = states.get(job.name)
        running = _is_locked(state, now)
        nxt = next_expected_run(job, state, now) if job.enabled else None
        never = state is None or state.last_started_at is None
        failing = bool(state and (state.consecutive_failures
                                  or (state.last_status == JobRun.STATUS_FAILED and not running)))
        overdue = bool(job.enabled and not running and not never and nxt and now > nxt + OVERDUE_SLACK)
        rows.append({
            'job': job, 'state': state, 'running': running, 'never': never,
            'failing': failing, 'overdue': overdue, 'next': nxt,
            'every': _every_label(job.every),
            'tick': 'quick + main' if job.name in QUICK_JOBS else 'main',
            'duration': _duration_label(state.last_duration_ms) if state and state.last_finished_at else '',
        })
    return rows


def _background(fn, *args):
    """Run ``fn`` on a daemon thread, closing its DB connection when done.

    A web request must not wait for a job (some take minutes), and the thread's
    connection would otherwise sit open until the worker recycles. Tests patch
    this to run inline.
    """
    def target():
        try:
            fn(*args)
        except Exception as exc:
            from core.errors import report
            report('DESK-9002', exc, context={'task': getattr(fn, '__name__', str(fn))})
        finally:
            connections.close_all()
    threading.Thread(target=target, name=f'staffdesk-{getattr(fn, "__name__", "job")}', daemon=True).start()


@staff_required
def jobs(request):
    now = timezone.now()
    rows = _job_rows(now)
    return render(request, 'staffdesk/ops/jobs.html', {
        'page_title': 'Background jobs', 'rows': rows, 'schedule': SCHEDULE_TEXT,
        'kpis': {
            'total': len(rows),
            'running': sum(r['running'] for r in rows),
            'failing': sum(r['failing'] for r in rows),
            'overdue': sum(r['overdue'] for r in rows),
        },
        'any_running': any(r['running'] for r in rows),
    })


@staff_required
@require_POST
def job_run(request, name):
    job = job_registry.JOBS_BY_NAME.get(name)
    if job is None:
        raise Http404('No such job')
    if _is_locked(JobRun.objects.filter(name=name).first(), timezone.now()):
        messages.info(request, f'{name} is already running.')
    else:
        _background(_run_forced, job)
        messages.success(request, f'{name} started. Refresh in a moment to see how it went.')
    return redirect('staffdesk:ops-jobs')


def _run_forced(job):
    runner.run_job(job, force=True)


@staff_required
@require_POST
def jobs_run_due(request):
    _background(runner.tick)
    messages.success(request, 'Running every job that is due. Each shows "running" until it finishes.')
    return redirect('staffdesk:ops-jobs')


# ===========================================================================
# Moderation
# ===========================================================================
MOD_TABS = ('violations', 'penalties', 'appeals', 'reputation')


def _review(violation, request, outcome):
    """Record who reviewed a violation in its evidence, for the paper trail."""
    evidence = dict(violation.evidence or {})
    evidence['review'] = {'outcome': outcome, 'by': request.user.email, 'at': timezone.now().isoformat()}
    violation.evidence = evidence
    violation.handled = True
    violation.save(update_fields=['evidence', 'handled'])


@staff_required
def moderation(request):
    tab = request.GET.get('tab') if request.GET.get('tab') in MOD_TABS else 'violations'
    term = (request.GET.get('q') or '').strip()
    show = request.GET.get('show', '')
    now = timezone.now()

    counts = {
        'violations': Violation.objects.filter(handled=False).count(),
        'penalties': Penalty.objects.filter(active=True).count(),
        'appeals': Appeal.objects.filter(status=Appeal.STATUS_PENDING).count(),
        'reputation': ReputationScore.objects.filter(score__lt=100).count(),
    }
    ctx = {'page_title': 'Moderation', 'tab': tab, 'search': term, 'show': show, 'counts': counts}

    if tab == 'violations':
        qs = Violation.objects.select_related('user__profile', 'message__group', 'reporter')
        qs = qs if show == 'all' else qs.filter(handled=False)
        if term:
            qs = qs.filter(_user_q('user__', term) | Q(text__icontains=term) | Q(category__icontains=term))
        qs = qs.annotate(n_penalties=Count('penalties')).order_by('-created_at')
    elif tab == 'penalties':
        qs = Penalty.objects.select_related('user__profile', 'violation', 'issued_by')
        qs = qs if show == 'all' else qs.filter(active=True)
        if term:
            qs = qs.filter(_user_q('user__', term) | Q(reason__icontains=term))
    elif tab == 'appeals':
        qs = Appeal.objects.select_related('user__profile', 'penalty', 'reviewed_by')
        qs = qs if show == 'all' else qs.filter(status=Appeal.STATUS_PENDING)
        if term:
            qs = qs.filter(_user_q('user__', term) | Q(message__icontains=term))
    else:
        qs = (ReputationScore.objects.select_related('user__profile')
              .annotate(n_violations=Count('user__violations', distinct=True),
                        n_penalties=Count('user__penalties', distinct=True))
              .order_by('score', '-updated_at'))
        if term:
            qs = qs.filter(_user_q('user__', term))

    page, querystring = _page(request, qs)
    ctx.update({'page': page, 'querystring': querystring, 'now': now})
    return render(request, 'staffdesk/ops/moderation.html', ctx)


@staff_required
@require_POST
def violation_action(request, pk):
    """Dismiss (a false positive) or confirm a flagged item.

    Dismissing undoes what :func:`~apps.communication.services.moderate_message`
    did automatically: lifts the penalties it issued, gives back the reputation
    and un-hides the message. Confirming a user report — which carries no
    automatic penalty — runs the normal penalty ladder.
    """
    violation = get_object_or_404(Violation.objects.select_related('message', 'user'), pk=pk)
    action = request.POST.get('action')
    auto = violation.detected_by != Violation.DETECTED_REPORT

    if action == 'dismiss':
        lifted = violation.penalties.filter(active=True).update(active=False)
        if auto:
            comms._adjust_reputation(violation.user, violation.score * 5)
            msg = violation.message
            if msg and msg.is_deleted and violation.score >= 3:
                msg.is_deleted = False
                msg.save(update_fields=['is_deleted'])
        _review(violation, request, 'dismissed')
        messages.success(request, f'Dismissed. {lifted} penalty(ies) lifted.' if lifted else 'Dismissed.')
    elif action == 'confirm':
        if not violation.penalties.exists():
            comms._adjust_reputation(violation.user, -violation.score * 5)
            penalty = comms.apply_penalty_ladder(violation.user, violation)
            penalty.issued_by = request.user
            penalty.save(update_fields=['issued_by'])
            note = f' {penalty.get_kind_display()} issued.'
        else:
            note = ''
        if request.POST.get('hide') and violation.message and not violation.message.is_deleted:
            violation.message.is_deleted = True
            violation.message.save(update_fields=['is_deleted'])
            note += ' Message hidden.'
        _review(violation, request, 'confirmed')
        messages.success(request, 'Confirmed.' + note)
    else:
        messages.error(request, 'Unknown action.')
    return _back(request, reverse('staffdesk:ops-moderation'))


@staff_required
@require_POST
def penalty_lift(request, pk):
    """Same as the admin's ``lift_penalties`` action, one at a time."""
    penalty = get_object_or_404(Penalty, pk=pk)
    if penalty.active:
        penalty.active = False
        penalty.save(update_fields=['active'])
        messages.success(request, f'{penalty.get_kind_display()} lifted for {display_name(penalty.user)}.')
    return _back(request, reverse('staffdesk:ops-moderation') + '?tab=penalties')


@staff_required
@require_POST
def appeal_decide(request, pk):
    """Approve (lifting the penalty) or deny an appeal, and tell the user why."""
    appeal = get_object_or_404(Appeal.objects.select_related('penalty', 'user'), pk=pk)
    form = AppealDecisionForm(request.POST)
    if appeal.status != Appeal.STATUS_PENDING or not form.is_valid():
        messages.error(request, 'That appeal has already been decided.' if form.is_valid()
                       else 'Choose approve or deny.')
        return _back(request, reverse('staffdesk:ops-moderation') + '?tab=appeals')

    approved = form.cleaned_data['decision'] == 'approve'
    appeal.status = Appeal.STATUS_ACCEPTED if approved else Appeal.STATUS_REJECTED
    appeal.reviewed_by = request.user
    appeal.save(update_fields=['status', 'reviewed_by'])
    if approved and appeal.penalty.active:
        appeal.penalty.active = False
        appeal.penalty.save(update_fields=['active'])

    # Appeal has no field for the reviewer's note, so it travels in the
    # notification — which is where the user would look for it anyway.
    note = form.cleaned_data['note'].strip()
    kind = appeal.penalty.get_kind_display().lower()
    comms.notify(
        appeal.user, actor=request.user, verb='appeal', email=True,
        level='success' if approved else 'info',
        title='Your appeal was approved' if approved else 'Your appeal was not upheld',
        body=(f'The {kind} has been lifted.' if approved else f'The {kind} stays in place.')
             + (f' {note}' if note else ''),
    )
    messages.success(request, f'Appeal {"approved" if approved else "denied"}; {display_name(appeal.user)} has been told.')
    return _back(request, reverse('staffdesk:ops-moderation') + '?tab=appeals')


# ===========================================================================
# Audit log
# ===========================================================================
def _audit_queryset(request):
    form = AuditFilterForm(request.GET or None)
    qs = ActivityLog.objects.select_related('actor__user', 'target_user__user')
    if form.is_bound and form.is_valid():
        f = form.cleaned_data
        if f['user']:
            term = f['user']
            qs = qs.filter(Q(actor__first_name__icontains=term) | Q(actor__last_name__icontains=term)
                           | Q(actor__user__email__icontains=term)
                           | Q(target_user__first_name__icontains=term)
                           | Q(target_user__last_name__icontains=term)
                           | Q(target_user__user__email__icontains=term))
        if f['action']:
            qs = qs.filter(action=f['action'])
        if f['date_from']:
            qs = qs.filter(timestamp__date__gte=f['date_from'])
        if f['date_to']:
            qs = qs.filter(timestamp__date__lte=f['date_to'])
        if f['q']:
            qs = qs.filter(Q(description__icontains=f['q']) | Q(request_path__icontains=f['q'])
                           | Q(ip_address__icontains=f['q']))
    return form, qs


def _person_label(person):
    if person is None:
        return ''
    return display_name(person.user) if person.user_id else f'{person.first_name} {person.last_name}'.strip()


@staff_required
def audit(request):
    form, qs = _audit_queryset(request)
    page, querystring = _page(request, qs)
    return render(request, 'staffdesk/ops/audit.html', {
        'page_title': 'Audit log', 'form': form, 'page': page, 'querystring': querystring,
        'total': page.paginator.count,
    })


class _Echo:
    def write(self, value):
        return value


@staff_required
def audit_export(request):
    """CSV of the filtered log, streamed so a large export does not sit in memory."""
    _, qs = _audit_queryset(request)
    writer = csv.writer(_Echo())

    def rows():
        yield writer.writerow(['Time (UTC)', 'Action', 'Actor', 'Actor e-mail', 'Target', 'Target e-mail',
                               'Description', 'IP address', 'Path'])
        for log in qs.iterator(chunk_size=2000):
            yield writer.writerow([
                log.timestamp.isoformat(), log.action,
                _person_label(log.actor), log.actor.user.email if log.actor and log.actor.user_id else '',
                _person_label(log.target_user),
                log.target_user.user.email if log.target_user and log.target_user.user_id else '',
                log.description, log.ip_address or '', log.request_path or '',
            ])

    response = StreamingHttpResponse(rows(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit-log-{timezone.localdate():%Y%m%d}.csv"'
    return response


# ===========================================================================
# Invitations & parent links
# ===========================================================================
INVITE_TABS = ('pending', 'accepted', 'revoked', 'all')

#: A pending invite older than this is flagged — the link still works (invites
#: never expire), but nobody has used it and it may be worth a nudge or revoke.
INVITE_STALE_DAYS = 30


@staff_required
def invitations(request):
    tab = request.GET.get('tab') if request.GET.get('tab') in INVITE_TABS else 'pending'
    term = (request.GET.get('q') or '').strip()
    qs = Invitation.objects.select_related('student__user', 'programme', 'invited_by', 'accepted_by')
    if tab != 'all':
        qs = qs.filter(status=tab)
    if term:
        qs = qs.filter(Q(email__icontains=term) | Q(student__first_name__icontains=term)
                       | Q(student__last_name__icontains=term) | Q(programme__name__icontains=term))
    page, querystring = _page(request, qs)
    stale_before = timezone.now() - timedelta(days=INVITE_STALE_DAYS)
    counts = {t: Invitation.objects.filter(status=t).count() for t in INVITE_TABS if t != 'all'}
    counts['all'] = sum(counts.values())
    return render(request, 'staffdesk/ops/invitations.html', {
        'page_title': 'Invitations', 'tab': tab, 'search': term, 'page': page,
        'querystring': querystring, 'counts': counts, 'stale_before': stale_before,
        'stale_days': INVITE_STALE_DAYS,
    })


@staff_required
@require_POST
def invitation_action(request, pk):
    invite = get_object_or_404(Invitation, pk=pk)
    action = request.POST.get('action')
    if not invite.is_open:
        messages.error(request, f'That invite is already {invite.get_status_display().lower()}.')
    elif action == 'resend':
        if account_emails.send_invite(invite):
            messages.success(request, f'Invite re-sent to {invite.email}.')
        else:
            messages.error(request, f'The e-mail to {invite.email} could not be sent — check the mail settings.')
    elif action == 'revoke':
        invite.status = Invitation.STATUS_REVOKED
        invite.save(update_fields=['status'])
        messages.success(request, f'Invite for {invite.email} revoked; the link no longer works.')
    else:
        messages.error(request, 'Unknown action.')
    return _back(request, reverse('staffdesk:ops-invitations'))


@staff_required
def parent_links(request):
    term = (request.GET.get('q') or '').strip()
    form = ParentLinkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        link = ParentLink.objects.create(parent=form.cleaned_data['parent'], student=form.cleaned_data['student'],
                                         relationship=form.cleaned_data['relationship'])
        messages.success(request, f'{display_name(link.parent)} is now linked to {display_name(link.student)}.')
        return redirect('staffdesk:ops-parent-links')

    qs = ParentLink.objects.select_related('parent__profile', 'student__profile')
    if term:
        qs = qs.filter(_user_q('parent__', term) | _user_q('student__', term) | Q(relationship__icontains=term))
    page, querystring = _page(request, qs)
    # How many parents each student on this page has, for the "1 of 2" column.
    student_ids = {link.student_id for link in page}
    per_student = dict(ParentLink.objects.filter(student_id__in=student_ids)
                       .values_list('student_id').annotate(n=Count('id')))
    for link in page:
        link.siblings = per_student.get(link.student_id, 0)

    User = get_user_model()
    return render(request, 'staffdesk/ops/parent_links.html', {
        'page_title': 'Parent links', 'form': form, 'search': term, 'page': page,
        'querystring': querystring, 'max_parents': ParentLink.MAX_PER_STUDENT,
        'total': ParentLink.objects.count(),
        'parent_emails': User.objects.filter(profile__user_type='parent').exclude(email='')
                             .order_by('email').values_list('email', flat=True)[:1000],
        'student_emails': User.objects.filter(profile__user_type='student').exclude(email='')
                              .order_by('email').values_list('email', flat=True)[:2000],
    })


@staff_required
@require_POST
def parent_link_remove(request, pk):
    link = get_object_or_404(ParentLink.objects.select_related('parent', 'student'), pk=pk)
    label = f'{display_name(link.parent)} → {display_name(link.student)}'
    link.delete()
    messages.success(request, f'Unlinked {label}.')
    return _back(request, reverse('staffdesk:ops-parent-links'))
