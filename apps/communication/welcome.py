"""The welcome pack — four notifications every new user gets when they finish
onboarding:

  1. a warm welcome into the United Church School family,
  2. a quick guide to where everything lives,
  3. a heads-up on the study timetable,
  4. who to talk to for what (academics → educators/staff, technical → admin).

Sent once per user (guarded on the ``welcome`` verb), so it is safe to call from
every place onboarding can complete — the student wizard and the staff/educator
first-login profile.
"""
import logging

logger = logging.getLogger('apps')


def send_welcome_pack(user):
    """Create the four welcome notifications for ``user`` — once. Idempotent and
    best-effort: never raises into the caller."""
    if user is None:
        return
    try:
        if user.notifications.filter(verb='welcome').exists():
            return
    except Exception:  # pragma: no cover - defensive
        return

    from .services import notify

    person = getattr(user, 'profile', None)
    name = ((getattr(person, 'first_name', '') or '').strip()
            or user.get_username())

    notify(user, verb='welcome', level='success',
           title=f'Welcome to the United Church School family, {name}! \U0001F331',
           body=("You've joined the United Church School learning platform — your classes, "
                 "lessons, homework, marks and messages from your teachers, all in one place. "
                 "United We Stand: learners, parents and teachers working together, and we're "
                 "genuinely glad you're here. Let's make this year count."),
           url='/myhub/')

    notify(user, verb='welcome', level='info',
           title='Quick guide — where to find everything',
           body=("A one-minute tour:\n"
                 "• Dashboard (home) — your feed, tasks and what's due next.\n"
                 "• My Subjects — everything you're registered for; open a subject for its Schedule.\n"
                 "• Schedule — the subject overview on top, then the weeks of the term, tests "
                 "and exams, each with its documents on the side.\n"
                 "• Messages & Notifications — stay in the loop with your teachers and class.\n"
                 "• Support (bottom of the sidebar) — how-to guides and answers to common questions."),
           url='/myhub/')

    notify(user, verb='welcome', level='info',
           title='Your timetable — what to look out for',
           body=("Each subject runs to the school calendar: terms, class tests, assignments "
                 "and examinations. Open your subject's Schedule to see the dates for your "
                 "grade, and watch Notifications — we'll remind you as each test and deadline "
                 "approaches so nothing sneaks up on you."),
           url='/calendar/')

    notify(user, verb='welcome', level='info',
           title='Who to talk to',
           body=("We're one message away:\n"
                 "• Academics — a topic, a mark, a lesson or the schedule — message your "
                 "teacher or the academic staff from Messages.\n"
                 "• Anything technical — logging in, school fees, or the platform itself — "
                 "contact the school office.\n"
                 "Never stuck in silence: reach out early and often."),
           url='/communication/chat/')
