"""Callable jobs — work that has no management command of its own.

Each returns a short string, which the runner records as that run's output so
``manage.py run_scheduled_jobs --list`` shows what actually happened.
"""


def run_deadline_reminders():
    """Create reminder notifications for work coming due."""
    from apps.communication import services

    created = services.scan_deadline_reminders()
    return f'{created} reminder(s) created'
