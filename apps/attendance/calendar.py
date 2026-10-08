"""School days for the daily register.

A school day is a weekday inside a school term that is not a public holiday or
a school holiday. ``core.school_calendar`` (term dates per year, holidays) is
the source of truth when it exists; otherwise this falls back to the 2026 term
dates in ``core.school.TERMS`` and the South African public holidays from
``core.academic_spine.public_holidays``.
"""

from datetime import date, datetime, time, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

SCHOOL_TZ = ZoneInfo('Africa/Johannesburg')

#: When the job opens the day's registers, and when it closes what is left open.
OPEN_AT = time(6, 30)
CLOSE_AT = time(17, 0)


def local_now():
    """Now, on the school's clock (independent of settings.TIME_ZONE)."""
    from django.utils import timezone
    return timezone.now().astimezone(SCHOOL_TZ)


def local_today():
    return local_now().date()


def _school_calendar():
    try:
        from core import school_calendar
    except ImportError:
        return None
    return school_calendar


def _calendar_verdict(day):
    """Ask core.school_calendar, if it is there. ``None`` = no answer (fall back)."""
    cal = _school_calendar()
    if cal is None:
        return None
    try:
        fn = getattr(cal, 'is_school_day', None)
        if callable(fn):
            return bool(fn(day))
        if day.weekday() >= 5:
            return False
        if day in _calendar_closed_days(day.year):
            return False
        year = cal.school_year(day.year)
        return any(first <= day <= last for _name, first, last in year.terms)
    except Exception:
        return None


@lru_cache(maxsize=16)
def _calendar_closed_days(year):
    """Public holidays plus whole-school holiday events (e.g. a special school
    holiday declared inside a term) from core.school_calendar."""
    cal = _school_calendar()
    days = {d for d, _name in cal.public_holidays(year)}
    for event in getattr(cal.school_year(year), 'events', []) or []:
        if getattr(event, 'kind', '') != getattr(cal, 'HOLIDAY', 'holiday'):
            continue
        if getattr(event, 'grades', None) is not None:
            continue
        start = event.start
        end = event.end or start
        while start <= end:
            days.add(start)
            start += timedelta(days=1)
    return frozenset(days)


@lru_cache(maxsize=16)
def _holidays(year):
    from core.academic_spine import public_holidays
    return frozenset(d for d, _name in public_holidays(year))


def _in_fallback_term(day):
    from core.school import TERMS
    for _name, (m1, d1), (m2, d2) in TERMS:
        if date(day.year, m1, d1) <= day <= date(day.year, m2, d2):
            return True
    return False


def is_school_day(day):
    """True when the school is open and a register should be taken on ``day``."""
    if isinstance(day, datetime):
        day = day.date()
    verdict = _calendar_verdict(day)
    if verdict is not None:
        return verdict
    if day.weekday() >= 5:
        return False
    if day in _holidays(day.year):
        return False
    return _in_fallback_term(day)


def school_days_between(start, end):
    """Every school day from ``start`` to ``end`` inclusive."""
    days, day = [], start
    while day <= end:
        if is_school_day(day):
            days.append(day)
        day += timedelta(days=1)
    return days


def week_start(day):
    return day - timedelta(days=day.weekday())
