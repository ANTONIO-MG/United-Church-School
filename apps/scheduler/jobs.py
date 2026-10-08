"""The job registry — what runs unattended, and how often.

Adding a job means adding one :class:`Job` to :data:`JOBS`. The runner
(``manage.py run_scheduled_jobs``) does the rest: interval checking, locking,
error capture and health bookkeeping.

A job is either a management command (``command='name'``, plus optional
``args``) or any importable callable (``dotted='pkg.mod:function'``). Callables
may return a string, which is recorded as the run's output.

Intervals are advisory: a job runs on the first tick *after* its interval has
elapsed, so the real cadence is bounded below by how often the runner ticks. One
cron entry every minute gives every job minute-level resolution.
"""

from dataclasses import dataclass, field

#: A held lock older than this is assumed to belong to a killed process.
LOCK_STALE_AFTER = 60 * 60      # 1 hour


@dataclass(frozen=True)
class Job:
    name: str
    every: int                              # seconds between runs
    description: str = ''
    command: str = ''                       # management command name
    args: tuple = ()                        # positional args for the command
    options: dict = field(default_factory=dict)   # keyword options for the command
    dotted: str = ''                        # 'pkg.module:callable' alternative
    enabled: bool = True

    def __post_init__(self):
        if bool(self.command) == bool(self.dotted):
            raise ValueError(f'Job {self.name!r} needs exactly one of command= or dotted=')


MINUTE = 60
HOUR = 60 * MINUTE


JOBS = [
    # --- Shop ------------------------------------------------------------
    Job(
        name='shop-bookings',
        every=5 * MINUTE,
        description='Release 1-on-1 slots held by orders that were never paid, and mark '
                    'sessions that have ended as completed.',
        dotted='apps.shop.booking:run_housekeeping',
    ),
    Job(
        name='shop-tracking',
        every=2 * HOUR,
        description='Refresh Courier Guy tracking for parcels on their way and tell buyers '
                    'when they are delivered. Idle until COURIER_GUY_API_KEY is set.',
        dotted='apps.shop.fulfilment:refresh_tracking',
    ),
    # --- Finance ---------------------------------------------------------
    Job(
        name='finance-daily',
        every=6 * HOUR,
        description='Invoice reminders (3 days before, on the day, 7 days after), expire '
                    'estimates past their date, and book recurring expenses that fell due.',
        dotted='apps.finance.documents:run_daily',
    ),
    # --- Attendance ------------------------------------------------------
    Job(
        name='finalise-attendance',
        every=15 * MINUTE,
        description='Close the register for ended class sessions: anyone below the '
                    'attendance threshold becomes absent and no-shows get a row.',
        command='finalise_attendance',
        options={'verbosity': 1},
    ),
    Job(
        name='sync-teams-meetings',
        every=15 * MINUTE,
        description='Pull finished Teams meetings — recording, transcript recap and the '
                    'Graph attendance report, which is authoritative for time in call.',
        command='sync_teams_meetings',
        options={'verbosity': 1},
    ),

    # --- Live sessions ---------------------------------------------------
    Job(
        name='session-pipeline',
        every=5 * MINUTE,
        description='Advance each finished session one step: poll Teams for the recording, '
                    'file it to OneDrive with the transcript and summary, publish it to the '
                    'module schedule, then upload it to YouTube when quota allows.',
        dotted='apps.livesessions.tasks:run_pipeline',
    ),
    Job(
        name='session-reminders',
        every=5 * MINUTE,
        description='Send the 24-hour and 30-minute reminders for upcoming sessions, each '
                    "rendered in the recipient's own time zone.",
        dotted='apps.livesessions.tasks:run_reminders',
    ),
    Job(
        name='session-ai-followup',
        every=30 * MINUTE,
        description='Have the admin Claude layer write the full session summary, the next '
                    "session's agenda and the action items, and file them to the module.",
        dotted='apps.livesessions.tasks:run_ai_followup',
    ),

    Job(
        name='calendar-subscriptions',
        every=30 * MINUTE,
        description='Re-import the Google / Outlook / Apple calendars users have connected, '
                    'so the school calendar and the free-slot finder see their real commitments.',
        dotted='apps.livesessions.tasks:run_calendar_subscriptions',
    ),

    # --- Reporting -------------------------------------------------------
    Job(
        name='rank-classes',
        every=6 * HOUR,
        description='Recompute persisted class positions and cohort averages.',
        command='rank_classes',
        options={'verbosity': 1},
    ),

    # --- Notifications ---------------------------------------------------
    Job(
        name='send-broadcasts',
        every=MINUTE,
        description='Send the notifications staff scheduled in the notifications centre once '
                    'their time comes.',
        dotted='apps.communication.broadcast:send_due',
    ),
    Job(
        name='auto-notices',
        every=10 * MINUTE,
        description='Tell students and educators about new material, lessons, videos, tests '
                    'opening, results, solutions and tasks — grouped per module, once each.',
        dotted='apps.communication.auto:run',
    ),
    Job(
        name='weekly-summary',
        every=HOUR,
        description='Monday from 06:00: each student\'s week ahead (deadlines, tests, classes, '
                    'new material, exam countdown) and each educator\'s teaching week.',
        dotted='apps.communication.weekly:run',
    ),
    Job(
        name='re-engagement',
        every=24 * HOUR,
        description='Nudge students who have not signed in for 7 days but still have work on '
                    '(at most once a fortnight each).',
        dotted='apps.communication.weekly:run_reengage',
    ),
    Job(
        name='risk-scan',
        every=24 * HOUR,
        description='Score every student for risk (inactivity, low marks, overdue work) and '
                    'open or update a flag for anyone at 30+, for the At-risk students page.',
        dotted='apps.staffdesk.views_academic:scan_risk',
    ),
    Job(
        name='database-backup',
        every=24 * HOUR,
        description='Make the daily restore point of the database (backups/db/; the last 30 '
                    'are kept) — see Staff desk → Backups.',
        dotted='apps.staffdesk.backups:scheduled_backup',
    ),
    Job(
        name='deadline-reminders',
        every=30 * MINUTE,
        description='Notify students about tasks, assessments and live sessions coming due.',
        dotted='apps.scheduler.tasks:run_deadline_reminders',
    ),
    Job(
        name='trial-ending-reminders',
        every=HOUR,
        description="E-mail students whose free week ends within 24 hours and whose "
                    "registration invoice is still unpaid — invoice attached, pay link "
                    "included. Sends once per invoice; skips anyone already settled or "
                    "marked paid by admin/staff.",
        dotted='apps.accounts.trial_reminders:send_trial_reminders',
    ),

    # --- Housekeeping ----------------------------------------------------
    Job(
        name='purge-closed-accounts',
        every=24 * HOUR,
        description='Delete soft-closed accounts whose 30-day grace period has elapsed.',
        command='purge_closed_accounts',
        options={'verbosity': 1},
    ),
]

JOBS_BY_NAME = {job.name: job for job in JOBS}
