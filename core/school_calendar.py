"""
core/school_calendar.py  —  United Church School's school year, 2026 and 2027.

The *facts* of the school calendar: terms, school holidays, public holidays and
every dated event, each tagged with the **grades** it applies to. Pure Python
(no Django); :mod:`core.academic_spine` turns it into ``AcademicCalendar`` /
``CalendarEvent`` rows and :mod:`apps.livesessions.academic` decides who sees
which row (a learner sees whole-school dates plus their own grade's).

Every event says whether it is **official** (published by the DBE, the GDE or
the school) or an **estimate** (the shape of the year from previous years, no
published date yet). Estimates are seeded unpublished — staff see them, learners
and parents do not until someone confirms the date in the admin.

Sources (checked 2026-10-08)
----------------------------
* DBE school calendar 2026 — Government Gazette No. 52177, Notice 5901
  (25 Feb 2025):
  https://www.education.gov.za/portals/0/documents/publications/2025/Published%202026%20School%20Calendar.pdf
  (copy: https://fedsas.org.za/FileHandler/d1f3a54b-9840-4abf-a415-1d38ab7e5f97)
* DBE school calendar 2027 — Government Gazette No. 52178, Notice 5902
  (25 Feb 2025; final, not a draft):
  https://www.education.gov.za/portals/0/documents/publications/2025/Published%202027%20School%20Calendar.pdf
  (copy: https://fedsas.org.za/FileHandler/25f44326-1f10-4bc8-929e-e14a3918f50f)
  The calendar is the same in all nine provinces, Gauteng included.
* NSC October/November 2026 timetable (DBE, final, February 2026):
  https://www.westerncape.gov.za/education/files/wcg-blob-files?file=2026-03%2Foct-nov-2026-nsc-timetable-final-february-2026.pdf&type=file
* May/June 2026 SC/NSC timetable (DBE, final, February 2026):
  https://www.education.gov.za/Portals/0/Documents/Publications/2026/May-June%202026%20SC_NSC%20TIMETABLE%20FINAL%20%20FEBRUARY%20%202026.pdf
* GDE Grade 12 preparatory examination timetable 2026 (reported):
  https://www.gauteng.net/whats-on-g/gauteng-grade-12-prelim-timetable-2026/
* GDE online admissions for 2027 (Grade 1 and Grade 8):
  https://www.ewn.co.za/gauteng-edu-dept-2027-online-applications-for-grades-1-and-8-open-from-5-august/
  and https://www.gauteng.net/whats-on-g/gde-2027-online-admissions/
* Local Government Elections Day, 4 November 2026 (once-off public holiday):
  https://www.sanews.gov.za/node/84344
* UCS prospectus 2026 ("School terms and times", "Fees 2026") via
  :mod:`core.school` — ``TERMS`` and ``FEE_DATES``.

UCS vs the official calendar, 2026
----------------------------------
UCS's prospectus term dates match the gazette for Terms 1 – 3 and the start of
Term 4. **Term 4 differs:** public schools close for learners on Wed 9 Dec 2026
(educators Fri 11 Dec); UCS, as an independent school, closes on Fri 11 Dec.
The UCS dates are used for 2026; 2027 uses the gazette (UCS has not published
its 2027 dates — revisit when it does).

Not published anywhere we could find (so written as estimates): the GDE June
and November examination windows for Grade 4 – 11, Foundation Phase assessment
weeks, GDE common tests, SBA/PAT moderation windows, report dates, everything
in the 2027 examination cycle and the 2028 admissions period.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from core import school

OFFICIAL, ESTIMATE = True, False

# Kinds — the same strings as apps.learning.models.CalendarEvent.KIND_*.
EXAM, TEST, SUPP, HOLIDAY, DEADLINE, ORIENTATION, RESULT, OTHER = (
    'exam', 'test', 'supp', 'holiday', 'deadline', 'orientation', 'result', 'other')

#: ``grades=None`` means the whole school.
WHOLE_SCHOOL = None
FOUNDATION = (1, 2, 3)
GRADES_4_TO_11 = tuple(range(4, 12))
GRADES_4_TO_12 = tuple(range(4, 13))
GRADES_1_TO_11 = tuple(range(1, 12))
MATRIC = (12,)

SRC_GAZETTE = {2026: 'DBE school calendar 2026 (GG 52177)',
               2027: 'DBE school calendar 2027 (GG 52178)'}
SRC_PROSPECTUS = 'UCS prospectus 2026'
SRC_NSC_2026 = 'DBE NSC Oct/Nov 2026 timetable (Feb 2026)'
SRC_GDE_PRELIM_2026 = 'GDE Grade 12 preparatory examination timetable 2026'
SRC_GDE_ADMISSIONS_2027 = 'GDE online admissions 2027 announcement'


@dataclass(frozen=True)
class Event:
    """One dated thing on the school calendar."""

    title: str
    kind: str
    start: date
    end: date = None
    #: ``None`` → whole school; else the grade numbers it applies to.
    grades: tuple = WHOLE_SCHOOL
    official: bool = OFFICIAL
    description: str = ''
    source: str = ''

    @property
    def whole_school(self):
        return self.grades is None


@dataclass
class SchoolYear:
    year: int
    #: ``[(name, first day, last day)]`` for learners.
    terms: list
    #: ``(first day, last day)`` for educators.
    educator_days: tuple = None
    #: Whether the term dates are published (prospectus or gazette).
    terms_official: bool = OFFICIAL
    terms_source: str = ''
    events: list = field(default_factory=list)

    def school_holidays(self, next_year=None):
        """``[Event]`` for the breaks between terms (and after the last term,
        up to the next year's first day when that year is known)."""
        out = []
        for (name, _, last), (_, nxt, _) in zip(self.terms, self.terms[1:]):
            out.append(Event(f'School holidays after {name}', HOLIDAY, last + timedelta(days=1),
                             nxt - timedelta(days=1), official=self.terms_official,
                             description='School closed.', source=self.terms_source))
        name, _, last = self.terms[-1]
        if next_year is not None:
            out.append(Event(f'School holidays after {name}', HOLIDAY, last + timedelta(days=1),
                             next_year.terms[0][1] - timedelta(days=1),
                             official=self.terms_official and next_year.terms_official,
                             description=f'End-of-year holidays. School reopens on '
                                         f'{next_year.terms[0][1]:%A %-d %B %Y}.',
                             source=self.terms_source))
        return out


# --------------------------------------------------------------------------
# Public holidays (Public Holidays Act 36 of 1994)
# --------------------------------------------------------------------------
FIXED_HOLIDAYS = [
    ((1, 1), "New Year's Day"),
    ((3, 21), 'Human Rights Day'),
    ((4, 27), 'Freedom Day'),
    ((5, 1), "Workers' Day"),
    ((6, 16), 'Youth Day'),
    ((8, 9), "National Women's Day"),
    ((9, 24), 'Heritage Day'),
    ((12, 16), 'Day of Reconciliation'),
    ((12, 25), 'Christmas Day'),
    ((12, 26), 'Day of Goodwill'),
]

#: Once-off holidays declared under s2A of the Act: ``{year: [(date, name)]}``.
SPECIAL_HOLIDAYS = {
    2026: [(date(2026, 11, 4), 'Local Government Elections Day')],
}


def easter_sunday(year):
    """Anonymous Gregorian computus — Good Friday and Family Day hang off this."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    lam = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * lam) // 451
    month = (h + lam - 7 * m + 114) // 31
    day = ((h + lam - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def public_holidays(year):
    """``[(date, name)]`` for the year: fixed days, the Easter pair, any once-off
    holiday, and the Monday after one that falls on a Sunday."""
    easter = easter_sunday(year)
    days = [(easter - timedelta(days=2), 'Good Friday'),
            (easter + timedelta(days=1), 'Family Day')]
    days += [(date(year, month, day), name) for (month, day), name in FIXED_HOLIDAYS]
    days += SPECIAL_HOLIDAYS.get(year, [])
    for when, name in list(days):
        if when.weekday() == 6:      # Sunday → the Monday is a public holiday too
            days.append((when + timedelta(days=1), f'{name} (observed)'))
    return sorted(days)


# --------------------------------------------------------------------------
# Recurring school items (fees, reports, term days)
# --------------------------------------------------------------------------
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December']


def _fee_events(year, official):
    """The fee policy's deadlines (core.school.FEE_DATES) plus the monthly fee
    due on the 1st of February – December (fees are paid January to December)."""
    source = SRC_PROSPECTUS if year == school.YEAR else 'UCS fee policy (2026 pattern)'
    out = [Event(title, DEADLINE, date(year, month, day), official=official,
                 description=note, source=source)
           for title, (month, day), note in school.FEE_DATES]
    for month in range(2, 13):
        out.append(Event(f'School fees due — {MONTHS[month - 1]}', DEADLINE, date(year, month, 1),
                         official=official, source=source,
                         description=f'{MONTHS[month - 1]} school fees are payable in advance by '
                                     f'the 1st. Subjects lock after the grace period if unpaid.'))
    return out


def _report_events(year_obj):
    """Report issuing on each term's last day (estimate — not published)."""
    out = []
    for index, (name, _, last) in enumerate(year_obj.terms):
        final = index == len(year_obj.terms) - 1
        out.append(Event(
            f'{name} reports issued', OTHER, last,
            grades=GRADES_1_TO_11 if final else WHOLE_SCHOOL, official=ESTIMATE,
            description=('Final reports and promotion decisions for Grade 1 – 11. Grade 12 '
                         'receive NSC results in January.' if final else
                         f'{name} progress reports go home on the last day of term.')))
    return out


# --------------------------------------------------------------------------
# 2026
# --------------------------------------------------------------------------
def _year_2026():
    y = 2026
    terms = [(name, date(y, *first), date(y, *last)) for name, first, last in school.TERMS]
    gaz = SRC_GAZETTE[y]
    yr = SchoolYear(y, terms, educator_days=(date(y, 1, 12), date(y, 12, 11)),
                    terms_source=SRC_PROSPECTUS + ' (matches ' + gaz + ' except Term 4 end)')
    yr.events = [
        Event('Educators return (schools open for staff)', OTHER, date(y, 1, 12), date(y, 1, 13),
              description='Staff preparation days before learners arrive on 14 January.',
              source=gaz),
        Event('Special school holiday', HOLIDAY, date(y, 6, 15),
              description='Gazetted school holiday (Monday before Youth Day) — school closed.',
              source=gaz),
        Event('Public schools close for learners (GDE)', OTHER, date(y, 12, 9),
              description='Public schools close on 9 December. UCS learners attend until '
                          'Friday 11 December, the last day of Term 4.', source=gaz),
        # -- Grade 12: NSC 2026 ------------------------------------------
        Event('Grade 12 Life Orientation Common Assessment Task (CAT)', EXAM, date(y, 9, 1),
              grades=MATRIC, description='NSC Life Orientation CAT, 09:00, 2½ hours.',
              source=SRC_NSC_2026),
        Event('Preliminary (trial) examinations', EXAM, date(y, 8, 25), date(y, 9, 18),
              grades=MATRIC, source=SRC_GDE_PRELIM_2026,
              description='GDE common Grade 12 preparatory examinations (first paper English / '
                          'Afrikaans FAL P2, last paper Life Sciences P2).'),
        Event('NSC pledge signing', OTHER, date(y, 10, 9), grades=MATRIC, source=SRC_NSC_2026,
              description='Candidates sign the NSC examination pledge.'),
        Event('Life Orientation CAT rewrite', EXAM, date(y, 10, 12), grades=MATRIC,
              source=SRC_NSC_2026, description='For candidates who missed the 1 September CAT.'),
        Event('NSC (matric) final examinations', EXAM, date(y, 10, 13), date(y, 11, 26),
              grades=MATRIC, source=SRC_NSC_2026,
              description='National Senior Certificate examinations to the DBE timetable: '
                          'CAT P1 practical on 13 October to Music P2 on 25 November; CAT/IT '
                          'practical rewrites 26 November. No papers 3 – 5 and 9 November.'),
        Event('NSC results released (Class of 2026)', RESULT, date(2027, 1, 13), grades=MATRIC,
              official=ESTIMATE,
              description='Expected mid-January 2027: the Minister announces the results the '
                          'evening before individual results are released.'),
        Event('May/June SC/NSC combined examinations', SUPP, date(y, 5, 11), date(y, 6, 26),
              grades=MATRIC, source='DBE May/June 2026 SC/NSC timetable (Feb 2026)',
              description='For candidates rewriting or completing NSC subjects (supplementary '
                          'and part-time candidates).'),
        # -- Grade 4 – 12: school examinations (not published) ----------------
        Event('Mid-year examinations', EXAM, date(y, 6, 1), date(y, 6, 19), grades=GRADES_4_TO_12,
              official=ESTIMATE,
              description='Term 2 controlled tests / mid-year examinations (15 June special '
                          'school holiday and 16 June Youth Day excluded).'),
        Event('Final examinations', EXAM, date(y, 11, 2), date(y, 11, 27), grades=GRADES_4_TO_11,
              official=ESTIMATE,
              description='Term 4 end-of-year examinations. No examination on Wednesday '
                          '4 November (Local Government Elections Day).'),
        # -- Foundation Phase ----------------------------------------------
        Event('Foundation Phase assessment week (mid-year)', TEST, date(y, 6, 8), date(y, 6, 19),
              grades=FOUNDATION, official=ESTIMATE,
              description='Grade 1 – 3 Term 2 formal assessment tasks (continuous assessment).'),
        Event('Foundation Phase assessment week (year-end)', TEST, date(y, 11, 16), date(y, 11, 27),
              grades=FOUNDATION, official=ESTIMATE,
              description='Grade 1 – 3 Term 4 formal assessment tasks (continuous assessment).'),
        # -- GDE admissions for 2027 (public schools) ------------------------
        Event('GDE online admissions for 2027 — Grade 8 applications', DEADLINE, date(y, 8, 5),
              date(y, 9, 4), grades=(7,), source=SRC_GDE_ADMISSIONS_2027,
              description='GDE online applications for Grade 8 in public schools: 5 August '
                          '08:00 to 4 September midnight. Continuing UCS learners re-register '
                          'with the school office instead.'),
        Event('GDE online admissions for 2027 — Grade 1 applications', DEADLINE, date(y, 8, 5),
              date(y, 9, 4), source=SRC_GDE_ADMISSIONS_2027,
              description='GDE online applications for Grade 1 in public schools (younger '
                          'siblings): 5 August to 4 September.'),
        Event('GDE admissions 2027 — certified documents due', DEADLINE, date(y, 9, 11),
              grades=(7,), source=SRC_GDE_ADMISSIONS_2027,
              description='Certified documents to the chosen public schools by 12:00.'),
        Event('GDE admissions 2027 — placement offers', OTHER, date(y, 10, 15), date(y, 10, 30),
              grades=(7,), source='GDE admissions phases (reported)',
              description='Placement offers by SMS; accept within 7 days.'),
    ]
    yr.events += _fee_events(y, OFFICIAL)
    yr.events += _report_events(yr)
    return yr


# --------------------------------------------------------------------------
# 2027 (the gazetted public-school calendar; UCS has not published its own yet)
# --------------------------------------------------------------------------
def _year_2027():
    y = 2027
    gaz = SRC_GAZETTE[y]
    terms = [('Term 1', date(y, 1, 13), date(y, 3, 19)),
             ('Term 2', date(y, 4, 6), date(y, 6, 25)),
             ('Term 3', date(y, 7, 20), date(y, 9, 22)),
             ('Term 4', date(y, 10, 5), date(y, 12, 8))]
    yr = SchoolYear(y, terms, educator_days=(date(y, 1, 11), date(y, 12, 10)), terms_source=gaz)
    est = ESTIMATE
    yr.events = [
        Event('Educators return (schools open for staff)', OTHER, date(y, 1, 11), date(y, 1, 12),
              description='Staff preparation days before learners arrive on 13 January.',
              source=gaz),
        Event('Special school holiday', HOLIDAY, date(y, 4, 26),
              description='Gazetted school holiday (Monday before Freedom Day) — school closed.',
              source=gaz),
        Event('Educators close (last staff day)', OTHER, date(y, 12, 10), source=gaz,
              description='Learners close on 8 December; staff on 10 December.'),
        # -- Grade 12: NSC 2027 (timetable not yet published) -----------------
        Event('May/June SC/NSC combined examinations', SUPP, date(y, 5, 10), date(y, 6, 25),
              grades=MATRIC, official=est,
              description='For candidates rewriting or completing NSC subjects.'),
        Event('Preliminary (trial) examinations', EXAM, date(y, 8, 24), date(y, 9, 17),
              grades=MATRIC, official=est,
              description='GDE common Grade 12 preparatory examinations.'),
        Event('Grade 12 Life Orientation Common Assessment Task (CAT)', EXAM, date(y, 9, 1),
              grades=MATRIC, official=est, description='NSC Life Orientation CAT.'),
        Event('NSC pledge signing', OTHER, date(y, 10, 8), grades=MATRIC, official=est,
              description='Candidates sign the NSC examination pledge.'),
        Event('NSC (matric) final examinations', EXAM, date(y, 10, 12), date(y, 11, 26),
              grades=MATRIC, official=est,
              description='National Senior Certificate examinations, written to the DBE '
                          'timetable (published around February 2027).'),
        Event('NSC results released (Class of 2027)', RESULT, date(2028, 1, 12), grades=MATRIC,
              official=est, description='Expected mid-January 2028.'),
        # -- Grade 4 – 12 school examinations ----------------------------------
        Event('Mid-year examinations', EXAM, date(y, 5, 31), date(y, 6, 18), grades=GRADES_4_TO_12,
              official=est, description='Term 2 controlled tests / mid-year examinations '
                                        '(16 June Youth Day excluded).'),
        Event('Final examinations', EXAM, date(y, 11, 1), date(y, 11, 26), grades=GRADES_4_TO_11,
              official=est, description='Term 4 end-of-year examinations.'),
        Event('Foundation Phase assessment week (mid-year)', TEST, date(y, 6, 7), date(y, 6, 18),
              grades=FOUNDATION, official=est,
              description='Grade 1 – 3 Term 2 formal assessment tasks (continuous assessment).'),
        Event('Foundation Phase assessment week (year-end)', TEST, date(y, 11, 15), date(y, 11, 26),
              grades=FOUNDATION, official=est,
              description='Grade 1 – 3 Term 4 formal assessment tasks (continuous assessment).'),
        # -- GDE admissions for 2028 (not yet announced) ----------------------
        Event('GDE online admissions for 2028 — Grade 8 applications', DEADLINE, date(y, 8, 4),
              date(y, 9, 3), grades=(7,), official=est,
              description='GDE online applications for Grade 8 in public schools (dates follow '
                          'the 2026 pattern; confirm when the GDE announces them).'),
        Event('GDE online admissions for 2028 — Grade 1 applications', DEADLINE, date(y, 8, 4),
              date(y, 9, 3), official=est,
              description='GDE online applications for Grade 1 in public schools (younger '
                          'siblings).'),
        Event('GDE admissions 2028 — placement offers', OTHER, date(y, 10, 14), date(y, 10, 29),
              grades=(7,), official=est, description='Placement offers by SMS.'),
    ]
    # The fee schedule for 2027 is not published: same deadlines as 2026, unconfirmed.
    yr.events += _fee_events(y, ESTIMATE)
    yr.events += _report_events(yr)
    return yr


YEARS = {2026: _year_2026(), 2027: _year_2027()}


def _template_year(year):
    """An unpublished outline for a year with no data yet: the latest known
    year's term days moved to ``year``, the public holidays and the fee dates."""
    latest = YEARS[max(YEARS)]

    def move(day):
        try:
            return day.replace(year=year)
        except ValueError:                     # 29 February
            return day.replace(year=year, day=28)

    yr = SchoolYear(year, [(n, move(a), move(b)) for n, a, b in latest.terms],
                    terms_official=ESTIMATE, terms_source='template')
    yr.events = _fee_events(year, ESTIMATE) + _report_events(yr)
    return yr


def school_year(year):
    """The :class:`SchoolYear` for ``year`` (a template for an unknown year)."""
    return YEARS.get(year) or _template_year(year)


def events_for(year):
    """Every :class:`Event` of the year in date order: terms, holidays (school and
    public) and the dated events."""
    yr = school_year(year)
    out = []
    for name, first, last in yr.terms:
        out.append(Event(f'{name} begins', ORIENTATION, first, official=yr.terms_official,
                         description=f'First day of {name} for learners.', source=yr.terms_source))
        out.append(Event(f'{name} ends', OTHER, last, official=yr.terms_official,
                         description=f'Last day of {name} for learners.', source=yr.terms_source))
    nxt = YEARS.get(year + 1)
    out += yr.school_holidays(nxt)
    # Public holidays are fixed by law (and the once-offs by proclamation): official.
    for when, name in public_holidays(year):
        out.append(Event(name, HOLIDAY, when, official=OFFICIAL,
                         description='South African public holiday — school closed.',
                         source=SRC_GAZETTE.get(year, 'Public Holidays Act 36 of 1994')))
    out += yr.events
    return sorted(out, key=lambda e: (e.start, e.title))


def grade_events(year, grade):
    """The events a learner in ``grade`` sees: whole-school plus their grade's."""
    return [e for e in events_for(year) if e.grades is None or grade in e.grades]
