"""The GDE school year in four terms — dates, labels and "which term is this?".

Term dates come from ``core.school_calendar`` when that module exists (it holds
the published calendar for more than one year); otherwise from
``core.school.TERMS`` (the 2026 prospectus), applied to whatever year is asked
for. Everything that has to place an assessment, a mark sheet or a report card
in a term goes through :func:`term_for` / :func:`term_dates`, so the calendar is
read in one place.
"""
import datetime

from core import school

TERM_NUMBERS = school.TERM_NUMBERS
EXAM_TERMS = school.EXAM_TERMS

TERM_LABELS = {1: 'Term 1', 2: 'Term 2', 3: 'Term 3', 4: 'Term 4'}
EXAM_LABELS = {2: 'Mid-year exam', 4: 'Final exam'}


def term_label(term):
    return TERM_LABELS.get(int(term), f'Term {term}')


def exam_label(term):
    """``Mid-year exam`` (Term 2) / ``Final exam`` (Term 4), else ``''``."""
    return EXAM_LABELS.get(int(term), '')


def _as_date(value, year):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, (tuple, list)) and len(value) == 2:      # (month, day)
        return datetime.date(year, int(value[0]), int(value[1]))
    if isinstance(value, str):
        return datetime.date.fromisoformat(value[:10])
    raise ValueError(f'Unrecognised term date {value!r}')


def _from_calendar(year, term):
    """Term dates from ``core.school_calendar`` (several shapes tolerated), or None."""
    try:
        from core import school_calendar as cal
    except Exception:
        return None
    try:
        school_year = getattr(cal, 'school_year', None)
        if callable(school_year):
            rows = list(getattr(school_year(year), 'terms', None) or [])
            if len(rows) >= term:
                _name, start, end = rows[term - 1]
                return _as_date(start, year), _as_date(end, year)
        fn = getattr(cal, 'term_dates', None)
        if callable(fn):
            found = fn(year, term)
            if found:
                start, end = found[0], found[1]
                return _as_date(start, year), _as_date(end, year)
        for name in ('TERMS', 'TERM_DATES', 'CALENDAR', 'TERMS_BY_YEAR'):
            table = getattr(cal, name, None)
            if not isinstance(table, dict) or year not in table:
                continue
            rows = table[year]
            if isinstance(rows, dict):
                row = rows.get(term) or rows.get(str(term))
            else:
                row = rows[term - 1] if len(rows) >= term else None
            if row is None:
                continue
            if isinstance(row, dict):
                start = row.get('start') or row.get('first_day') or row.get('opens')
                end = row.get('end') or row.get('last_day') or row.get('closes')
            else:
                row = list(row)
                if row and isinstance(row[0], str) and not row[0][:1].isdigit():
                    row = row[1:]                                  # drop a 'Term 1' label
                start, end = row[0], row[1]
            return _as_date(start, year), _as_date(end, year)
    except Exception:
        return None
    return None


def term_dates(year, term):
    """``(first day, last day)`` of ``term`` in ``year``."""
    year, term = int(year), int(term)
    if term not in TERM_NUMBERS:
        raise ValueError(f'No term {term!r}')
    found = _from_calendar(year, term)
    if found:
        return found
    _label, start, end = school.TERMS[term - 1]
    return _as_date(start, year), _as_date(end, year)


def term_for(day=None):
    """``(year, term)`` a date belongs to.

    A date in a school holiday belongs to the term that has just ended (work
    set over the holiday is reported with it); a date before Term 1 belongs to
    Term 1 of that year.
    """
    if day is None:
        from django.utils import timezone
        day = timezone.localdate()
    if isinstance(day, datetime.datetime):
        from django.utils import timezone
        if timezone.is_aware(day):
            day = timezone.localtime(day)
        day = day.date()
    year = day.year
    current = 1
    for term in TERM_NUMBERS:
        start, _end = term_dates(year, term)
        if day >= start:
            current = term
    return year, current


def term_window(year, term):
    """``(start, end)`` used to *bucket* dates into a term: from the first day
    of the term up to the day before the next term begins (Term 4 runs to the
    end of the year, Term 1 from 1 January), so holiday work is never lost."""
    year, term = int(year), int(term)
    start = datetime.date(year, 1, 1) if term == 1 else term_dates(year, term)[0]
    if term == TERM_NUMBERS[-1]:
        end = datetime.date(year, 12, 31)
    else:
        end = term_dates(year, term + 1)[0] - datetime.timedelta(days=1)
    return start, end


def current_year_term():
    return term_for(None)
