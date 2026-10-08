"""The Claude layer over a finished session: write-up, next agenda, action items.

The extractive recap :mod:`apps.msteams.recap` produces is fast, free and shallow
— it picks sentences out of the transcript. This is the other half: once the
session folder holds the transcript and the Microsoft summary, the **admin**
Claude layer reads them and produces the things a teacher would otherwise write by
hand on a Sunday evening:

1. a full written summary of what the session actually covered;
2. an **agenda for the next session**, built from what was left unfinished;
3. **action items**, split between the students and the educator.

Three deliberate constraints:

* **Admin layer only.** :mod:`apps.ai_assistant.admin_ai` is the paid, token-billed
  Claude tier reserved for admins and staff. This job runs on that layer under the
  platform's own admin identity — never on a student's or an educator's account,
  and never in a request. It is a background job precisely so nobody's page waits
  on it and no student's session can spend admin tokens.
* **Filed, not broadcast.** The output goes back into the same places the rest of
  the session's material lives: the session's OneDrive folder, an
  :class:`~apps.ai_assistant.models.AiReport` on the module, and the module's
  Documents tab. Reminders are then created from the action items.
* **Never destructive.** If Claude is unconfigured, rate-limited or returns
  nonsense, the session keeps its extractive recap and the job simply tries
  again next time. Nothing already filed is overwritten with an error.
"""

import json
import logging

from django.utils import timezone

logger = logging.getLogger('apps')

PROMPT = """You are preparing the follow-up pack for a live online class at United Church \
School, a Grade 1-12 school in Johannesburg following the South African CAPS curriculum. You are given the session's \
details and its transcript-derived material.

Produce STRICT JSON with exactly these keys and no prose outside the JSON:

{
  "summary_markdown": "A full written summary of the session in Markdown. Cover what \
was taught, the worked examples, the standards or sections referenced, the questions \
learners asked and how they were answered, and anything explicitly left for next time. \
Write for a learner who missed the session and needs to catch up without watching it.",
  "next_agenda": ["Ordered agenda items for the NEXT session, each a full sentence, \
built from what was unfinished, misunderstood or promised."],
  "student_actions": [{"task": "...", "due_hint": "before the next session | this week | \
before the test", "why": "one clause on why it matters"}],
  "educator_actions": [{"task": "...", "due_hint": "...", "why": "..."}],
  "topics_covered": ["short topic or standard references, e.g. quadratic equations, photosynthesis"],
  "concerns": ["anything suggesting a learner is struggling, or empty"]
}

Rules:
- Ground everything in the material provided. Do not invent examples, marks or dates.
- The attendance roster gives you real names and e-mail addresses. Use the names when attributing a question or a contribution, but only when the transcript makes it clear who spoke. Never put an e-mail address in the summary, and never guess who said something.
- If the material is too thin to answer a key, use an empty list or a short honest note.
- Keep each action item to one concrete, checkable thing.
"""


def is_enabled():
    from apps.ai_assistant import admin_ai
    from .models import LiveSessionSettings
    return bool(LiveSessionSettings.load().ai_followup_enabled and admin_ai.is_enabled())


def run(limit=5):
    """Process up to ``limit`` published sessions that have no follow-up yet."""
    from .models import SessionArtifact

    if not is_enabled():
        return 'AI follow-up is off or the admin Claude layer is not configured'

    pending = (SessionArtifact.objects
               .filter(state=SessionArtifact.STATE_PUBLISHED, ai_followup_done=False)
               .select_related('meeting', 'meeting__module', 'meeting__host')
               .order_by('published_at')[:limit])

    done, skipped = 0, 0
    for artifact in pending:
        try:
            if process(artifact):
                done += 1
            else:
                skipped += 1
        except Exception:
            logger.exception('livesessions: AI follow-up failed for %s', artifact.meeting)
            skipped += 1
    return f'{done} follow-up pack(s) written, {skipped} skipped'


def process(artifact):
    """Generate and file one session's follow-up pack. True if it wrote one."""
    from apps.ai_assistant import admin_ai

    meeting = artifact.meeting
    material = _source_material(artifact)
    if len(material.strip()) < 200:
        # Nothing worth spending admin tokens on. Mark it done so the job does
        # not keep re-reading a two-line transcript every hour.
        artifact.ai_followup_done = True
        artifact.save(update_fields=['ai_followup_done', 'updated_at'])
        return False

    question = f'{PROMPT}\n\nSESSION\n{_session_header(meeting)}\n\nMATERIAL\n{material[:120000]}'
    answer, _usage = admin_ai.ask([], question)
    pack = _parse(answer)
    if not pack:
        logger.warning('livesessions: Claude returned no usable JSON for %s', meeting)
        return False

    report = _file_report(artifact, pack)
    _file_to_onedrive(artifact, pack)
    _file_to_module_documents(artifact, report)
    _create_reminders(artifact, pack)

    artifact.ai_followup_done = True
    artifact.ai_report_id = getattr(report, 'pk', None)
    artifact.save(update_fields=['ai_followup_done', 'ai_report_id', 'updated_at'])
    return True


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------
def _session_header(meeting):
    """The facts Claude needs to write in the right register."""
    rows = [
        ('Title', meeting.title),
        ('Kind', meeting.get_session_kind_display()),
        ('Institution', getattr(meeting.resolved_institution, 'display_name', '')),
        ('Programme', getattr(meeting.resolved_programme, 'label', '')),
        ('Module', meeting.module.display_name if meeting.module_id else ''),
        ('Week / topic', meeting.week.display_title if meeting.week_id else ''),
        ('Prepares for', meeting.calendar_event.title if meeting.calendar_event_id else ''),
        ('Held', f'{timezone.localtime(meeting.scheduled_start):%A %d %B %Y, %H:%M}'
                 if meeting.scheduled_start else ''),
        ('Duration', f'{meeting.duration_minutes} minutes'),
        ('Description', meeting.description),
    ]
    header = '\n'.join(f'{k}: {v}' for k, v in rows if v)
    roster = attendance_roster(meeting)
    return f'{header}\n\nWHO ATTENDED\n{roster}' if roster else header


def attendance_roster(meeting):
    """Who was in the session, by name and e-mail, with how long they stayed.

    Drawn from the platform's own register, not from what people typed into
    Teams: students join anonymously, so the Graph report on its own is a list of
    nicknames. This is what puts real, checkable identities into the summary —
    and it is what lets the model say "Thabo asked about deferred tax" instead of
    "an attendee asked".
    """
    session = getattr(meeting, 'class_session', None)
    if session is None:
        return ''

    lines = []
    for record in (session.attendance
                   .select_related('student', 'student__profile')
                   .order_by('-seconds_attended')):
        student = record.student
        name = (student.get_full_name() or '').strip() or student.get_username()
        person = getattr(student, 'profile', None)
        if person is not None and (person.first_name or person.last_name):
            name = f'{person.first_name} {person.last_name}'.strip()
        lines.append(f'- {name} <{student.email}> — {record.minutes_attended} min '
                     f'({record.attended_pct}%), {record.get_status_display().lower()}')
    return '\n'.join(lines)


def _source_material(artifact):
    """The extractive recap plus the raw transcript, as one blob.

    Both, not either: the recap is structured but lossy, and the transcript has
    the detail but no shape. Claude gets to use the recap as an outline and the
    transcript as the evidence.
    """
    from apps.msteams import graph
    from .pipeline import recap_markdown

    meeting = artifact.meeting
    parts = []
    recap = recap_markdown(meeting)
    if recap:
        parts.append('## Automatic recap\n' + recap)

    if meeting.organizer_upn and meeting.teams_meeting_id and graph.is_configured():
        for transcript in graph.list_transcripts(meeting.organizer_upn, meeting.teams_meeting_id):
            content = graph.get_transcript_content(
                meeting.organizer_upn, meeting.teams_meeting_id, transcript.get('id'))
            if content:
                parts.append('## Transcript\n' + content)
    return '\n\n'.join(parts)


def _parse(answer):
    """Pull the JSON object out of Claude's reply, tolerating a code fence."""
    if not answer:
        return None
    text = answer.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1]
        text = text.rsplit('```', 1)[0]
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end <= start:
        return None
    try:
        pack = json.loads(text[start:end + 1])
    except ValueError:
        return None
    return pack if isinstance(pack, dict) and pack.get('summary_markdown') else None


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------
def _markdown(meeting, pack):
    """The whole pack as one readable document."""
    lines = [f'# {meeting.title}', '', _session_header(meeting), '',
             '## Session summary', '', pack.get('summary_markdown', '').strip(), '']

    agenda = pack.get('next_agenda') or []
    if agenda:
        lines += ['## Agenda for the next session', '']
        lines += [f'{i}. {item}' for i, item in enumerate(agenda, 1)] + ['']

    for heading, key in (('Action items — learners', 'student_actions'),
                         ('Action items — teacher', 'educator_actions')):
        items = pack.get(key) or []
        if not items:
            continue
        lines += [f'## {heading}', '']
        for item in items:
            task = item.get('task') if isinstance(item, dict) else str(item)
            due = (item.get('due_hint') or '') if isinstance(item, dict) else ''
            why = (item.get('why') or '') if isinstance(item, dict) else ''
            suffix = ' — '.join(x for x in (due, why) if x)
            lines.append(f'- [ ] {task}' + (f' ({suffix})' if suffix else ''))
        lines.append('')

    roster = attendance_roster(meeting)
    if roster:
        lines += ['## Who attended', '', roster, '']

    topics = pack.get('topics_covered') or []
    if topics:
        lines += ['## Topics covered', '', ', '.join(str(t) for t in topics), '']
    concerns = pack.get('concerns') or []
    if concerns:
        lines += ['## Flags', ''] + [f'- {c}' for c in concerns] + ['']
    return '\n'.join(lines)


def _file_report(artifact, pack):
    """Store the pack as an AiReport on the module."""
    from apps.ai_assistant.models import AiReport

    meeting = artifact.meeting
    report, _ = AiReport.objects.update_or_create(
        linked_ref=f'session-followup:{meeting.pk}',
        defaults={
            'kind': AiReport.KIND_MEETING_RECAP,
            'title': f'Session pack — {meeting.title}',
            'module': meeting.module,
            'created_by': meeting.host,
            'prompt': 'Automated post-session follow-up (admin Claude layer).',
            'content': _markdown(meeting, pack),
            'data': pack,
            'used_llm': True,
            'status': AiReport.STATUS_FINAL,
        },
    )
    return report


def _file_to_onedrive(artifact, pack):
    """Drop the pack into the session's own folder, beside the video."""
    from apps.msteams import onedrive
    from .pipeline import folder_ref

    folder = folder_ref(artifact)
    if not folder:
        return False
    name = f'{onedrive.artifact_stem(artifact.meeting)}-session-pack.md'
    return bool(onedrive.put_text(folder, name, _markdown(artifact.meeting, pack), 'text/markdown'))


def _file_to_module_documents(artifact, report):
    """Surface the pack on the module's Documents tab as a normal material row."""
    meeting = artifact.meeting
    if not meeting.module_id or report is None:
        return None
    from apps.learning.models import ModuleMaterial
    from .pipeline import phase_for

    phase = phase_for(meeting)
    if phase is None:
        return None
    material, _ = ModuleMaterial.objects.update_or_create(
        phase=phase,
        kind=ModuleMaterial.KIND_DOCUMENT,
        title=f'Session pack — {meeting.title}',
        defaults={
            'week': meeting.week if meeting.week_id and meeting.week.phase_id == phase.pk else None,
            'description': 'Full summary, next-session agenda and action items.',
            # The session page renders the pack alongside the recording and the
            # transcript, so the document row points there rather than at a
            # standalone report view that would show the pack out of context.
            'meeting': meeting,
            'url': meeting.get_absolute_url(),
        },
    )
    return material


def _create_reminders(artifact, pack):
    """Turn the action items into real tasks for the people they belong to.

    Candidates get the student actions, the educator gets theirs. They become
    ``tasks.Task`` rows so they show up in the existing "My Tasks" surface and
    are swept by the existing deadline-reminder job — rather than becoming a
    fourth kind of to-do nobody looks at.
    """
    meeting = artifact.meeting
    try:
        from apps.tasks.models import Task, TaskAssignment
    except Exception:       # pragma: no cover - tasks app is optional
        return 0

    from .audience import student_recipients_for

    created = 0
    due = _next_session_start(meeting)

    student_actions = [a for a in (pack.get('student_actions') or []) if _task_text(a)]
    if student_actions:
        students = list(student_recipients_for(meeting))
        for action in student_actions[:10]:
            task = _get_or_make_task(Task, meeting, _task_text(action), due)
            if task is None:
                continue
            for user in students:
                _, made = TaskAssignment.objects.get_or_create(task=task, user=user)
                created += int(made)

    educator_actions = [a for a in (pack.get('educator_actions') or []) if _task_text(a)]
    if educator_actions and meeting.host_id:
        for action in educator_actions[:10]:
            task = _get_or_make_task(Task, meeting, _task_text(action), due)
            if task is None:
                continue
            _, made = TaskAssignment.objects.get_or_create(task=task, user=meeting.host)
            created += int(made)
    return created


def _task_text(action):
    if isinstance(action, dict):
        return (action.get('task') or '').strip()
    return str(action or '').strip()


def _get_or_make_task(Task, meeting, title, due):
    """One task per (module, title). Never duplicated on a re-run.

    Matching on the module as well as the title matters: "Rework question 3" is
    a plausible action item on four different modules, and keying on the title
    alone would quietly hand Taxation candidates the Financial Reporting task.
    """
    try:
        task, _ = Task.objects.get_or_create(
            title=title[:200],
            module=meeting.module,
            defaults={
                'description': f'From the session pack for “{meeting.title}”.',
                'due_date': due,
                'created_by': meeting.host,
                'assign_to': Task.ASSIGN_SUBJECT if meeting.module_id else Task.ASSIGN_USER,
            },
        )
        return task
    except Exception:
        logger.exception('livesessions: could not create the follow-up task %r', title)
        return None


def _next_session_start(meeting):
    """When the next session on the same module is — the natural due date."""
    from apps.communication.models import MeetingRoom
    if not meeting.module_id or not meeting.scheduled_start:
        return None
    nxt = (MeetingRoom.objects
           .filter(module_id=meeting.module_id, is_active=True,
                   scheduled_start__gt=meeting.scheduled_start)
           .order_by('scheduled_start').first())
    return getattr(nxt, 'scheduled_start', None)
