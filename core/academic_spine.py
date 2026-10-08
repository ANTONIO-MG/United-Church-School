"""
core/academic_spine.py  —  United Church School's academic spine, built.

The school, its twelve grades, the CAPS subjects offered in each grade, each
grade's 2026 fee schedule, the year's class per grade and the school calendar.
The *facts* live in :mod:`core.school` (from www.ucs.org.za and the UCS
Application Form 2026); this module turns them into rows.
``.admin_wipe_and_create.py`` installs it as part of a fresh build and
``.demo_seed.py`` enrols its demo learners and teachers into what it created.

What ``seed()`` creates
-----------------------
* **1 institution** — United Church School (``UCS``), with the school crest as
  its logo (``static/images/brand/ucs-crest.png``) and its navy accent.
* **12 programmes** — Grade 1 to Grade 12 (``UCS-GR01`` … ``UCS-GR12``), each in
  its CAPS phase and carrying its fee band: registration (new learners), annual
  levy and monthly school fees (United Church School Fees 2026).
* **The canonical subject catalogue** — English Home Language, isiZulu and
  Afrikaans FAL, Mathematics, Mathematical Literacy, Life Skills, the
  Senior-Phase subjects, the FET electives and Coding and Robotics.
* **Subject offerings in every grade**, per the 2026 prospectus. Grade 10 – 12
  offerings carry their choice group (one FAL, Mathematics or Mathematical
  Literacy, three electives); everything else is compulsory. Subjects carry no
  price of their own — the grade's school fees pay for them.
* **A class per grade for the year** (cohort ``2026``, "Grade 5 · 2026").
* **The school calendar** — the four terms (opening and closing days, from the
  prospectus), the holidays between them, the fee deadlines, South Africa's
  public holidays, and a template of the June and November examination windows.

⚠️  **The examination windows are a template, not the school's timetable.** The
prospectus publishes the term dates (those are written ``is_published=True``)
but not the exam timetable, so the exam windows are written unpublished unless
``publish=True`` and say so in their description. Replace them from the real
timetable in the Django admin (Learning → Academic calendars).

Using it
--------
    from core import academic_spine

    result = academic_spine.seed()                       # everything, school year
    result = academic_spine.seed(year=2027)              # next year's calendar + class
    result = academic_spine.seed(calendar=False)         # spine only, fast

    # putting people on it (see .demo_seed.py)
    for person, programme in academic_spine.allocate_students(students):
        academic_spine.enrol_student(person, programme)

Seeding is idempotent and non-destructive: it creates what is missing and leaves
existing rows alone. With ``update=False`` (the default) it only fills blanks, so
edits made in the admin survive a re-run; ``update=True`` re-applies the facts
(e.g. after editing a fee in :mod:`core.school`).
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.learning.models import (
    DEPTH_ADVANCED, DEPTH_FOUNDATIONAL,
    AcademicCalendar, CalendarEvent, Cohort, Institution, Module,
    ModuleEnrolment, Programme, ProgrammeEnrolment, ProgrammeModule,
)
from core import school

#: What a subject costs on top of the grade's school fees, per month. Nothing.
DEFAULT_PRICE = Decimal('0')

#: The school crest, used as the institution logo.
CREST = Path(settings.BASE_DIR) / 'static' / 'images' / 'brand' / 'ucs-crest.png'

_LEVEL_FOR_PHASE = {
    school.PHASE_FOUNDATION: Programme.LEVEL_FOUNDATION,
    school.PHASE_INTERMEDIATE: Programme.LEVEL_INTERMEDIATE,
    school.PHASE_SENIOR: Programme.LEVEL_SENIOR,
    school.PHASE_FET: Programme.LEVEL_FET,
}


def grade_spec(grade):
    """The Programme fields for one grade, built from :mod:`core.school`."""
    phase = school.phase_for(grade)
    band = school.fee_band(grade)
    name = f'Grade {grade}'
    return {
        'code': school.grade_code(grade),
        'name': name, 'full_name': name, 'abbreviation': name,
        'grade': grade, 'order': grade,
        'level': _LEVEL_FOR_PHASE[phase['code']],
        'depth_default': DEPTH_FOUNDATIONAL if grade <= 3 else DEPTH_ADVANCED,
        'registration_fee': band['registration'],
        'annual_levy': band['levy'],
        'monthly_fee': band['monthly'],
        'description': (
            f"{name} at United Church School — {phase['name']}, {phase['school']} "
            f"({phase['campus']}). CAPS curriculum with English as the medium of instruction. "
            f"Fees {school.YEAR}: R{band['monthly']:,.0f} per month (January to December) plus an "
            f"annual levy of R{band['levy']:,.0f}"
            + (f" and a once-off registration fee of R{band['registration']:,.0f} for new learners."
               if band['registration'] else '.')
        ).replace(',', ' '),
    }


#: (title, kind, (month, day), span in days, note) — exam windows per phase.
#: A template: the prospectus does not publish the exam timetable.
EXAM_WINDOWS = {
    'mid-year': ('Mid-year examinations', CalendarEvent.KIND_EXAM, (6, 1), 19,
                 'Term 2 controlled tests / mid-year examinations.'),
    'final': ('Final examinations', CalendarEvent.KIND_EXAM, (11, 2), 26,
              'Term 4 final examinations and assessments.'),
    'nsc': ('NSC (matric) final examinations', CalendarEvent.KIND_EXAM, (10, 20), 36,
            'National Senior Certificate examinations, written to the Department of Basic '
            'Education timetable.'),
    'prelim': ('Preliminary (trial) examinations', CalendarEvent.KIND_EXAM, (8, 24), 19,
               'Grade 12 preliminary examinations ahead of the NSC.'),
}

# South African public holidays — fixed-date ones; the Easter pair is computed.
# Where one falls on a Sunday the following Monday is a public holiday too
# (Public Holidays Act 36 of 1994).
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

# --------------------------------------------------------------------------
# How the demo learners are spread across the grades: evenly, Grade 1 – 12.
# (institution code, programme code, share)
# --------------------------------------------------------------------------
STUDENT_ALLOCATION = [(school.SCHOOL['code'], school.grade_code(g), 1 / 12) for g in school.GRADES]


# --------------------------------------------------------------------------
# Blueprints — what the staff "Add institution" form can build in one go.
# --------------------------------------------------------------------------
BLUEPRINTS = {
    'school': {
        'label': 'School — Grade 1 to Grade 12 with CAPS subjects and fees',
        'summary': 'Twelve grades in their CAPS phases, every subject the UCS prospectus offers per '
                   'grade (with the Grade 10 – 12 subject choices), and the 2026 fee schedule.',
    },
    'blank': {
        'label': 'Blank — I will add the grades myself',
        'summary': 'Creates the school only. Add its grades and subjects from the school page '
                   'afterwards.',
    },
}

#: ``[(key, label)]`` for a form's choice field, blank last.
BLUEPRINT_CHOICES = [(key, spec['label']) for key, spec in BLUEPRINTS.items()]


def apply_blueprint(institution, key, *, price=DEFAULT_PRICE, calendar=True, year=None,
                    publish=False):
    """Build ``key``'s grades and subjects under ``institution``.

    Returns ``{'programmes': [...], 'offerings': [...], 'events': int}``.
    """
    if key != 'school':
        return {'programmes': [], 'offerings': [], 'events': 0}
    seeder = SpineSeeder(year=year, price=price, publish=publish, verbose=False, logos=False)
    modules = seeder.seed_modules()
    programmes, offerings = seeder.seed_programmes(institution, modules)
    events = seeder.seed_calendar(institution) if calendar else 0
    return {'programmes': list(programmes.values()), 'offerings': offerings, 'events': events}


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
    """``[(date, name)]`` for the year, Sunday roll-over applied."""
    easter = easter_sunday(year)
    days = [(easter - timedelta(days=2), 'Good Friday'),
            (easter + timedelta(days=1), 'Family Day')]
    days += [(date(year, month, day), name) for (month, day), name in FIXED_HOLIDAYS]
    for when, name in list(days):
        if when.weekday() == 6:      # Sunday → the Monday is a public holiday too
            days.append((when + timedelta(days=1), f'{name} (observed)'))
    return sorted(days)


def crest_png():
    """The school crest as PNG bytes (``None`` if the static file is missing)."""
    try:
        return CREST.read_bytes()
    except OSError:
        return None


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------
PROVISIONAL = ('\n\nTemplate date — the school has not published its examination timetable. '
               'Confirm against the official timetable and correct it here.')


class SpineSeeder:
    """Builds the spine. See :func:`seed` for the usual way in."""

    def __init__(self, *, year=None, price=DEFAULT_PRICE, update=False, logos=True,
                 refresh_logos=False, calendar=True, holidays=True, publish=False,
                 verbose=True, indent='  '):
        self.year = year or school.YEAR
        self.price = Decimal(str(price))
        self.update = update
        self.logos = logos
        self.refresh_logos = refresh_logos
        self.calendar = calendar
        self.holidays = holidays
        self.publish = publish
        self.verbose = verbose
        self.indent = indent

    # -- helpers ----------------------------------------------------------
    def log(self, message):
        if self.verbose:
            print(f'{self.indent}{message}')

    def _apply(self, obj, fields, created):
        """Write ``fields`` onto ``obj``. On an existing row only blanks are
        filled, unless ``update=True`` — so admin edits survive a re-run."""
        changed = []
        for name, value in fields.items():
            current = getattr(obj, name)
            if created or self.update or current in ('', None, 0):
                if current != value:
                    setattr(obj, name, value)
                    changed.append(name)
        if changed:
            obj.save()
        return changed

    # -- the school ---------------------------------------------------------
    def seed_institution(self):
        spec = dict(school.SCHOOL)
        code = spec.pop('code')
        institution, created = Institution.objects.get_or_create(
            code=code, defaults={'name': spec['name']})
        self._apply(institution, {**spec, 'order': 1, 'is_active': True}, created)
        if self.logos and (not institution.logo or self.refresh_logos):
            png = crest_png()
            if png:
                institution.logo.save('ucs-crest.png', ContentFile(png), save=True)
        self.log(f'  institution  {institution.code} — {institution.name}')
        return institution

    # -- subjects -----------------------------------------------------------
    def seed_modules(self):
        made = {}
        for spec in school.SUBJECTS:
            spec = dict(spec)
            code = spec.pop('code')
            module, created = Module.objects.get_or_create(code=code, defaults={'name': spec['name']})
            self._apply(module, spec, created)
            made[code] = module
        self.log(f'  {len(made)} subjects in the catalogue')
        return made

    # -- grades, subject offerings, classes ---------------------------------
    def seed_programmes(self, institution, modules):
        programmes, offerings = {}, []
        for grade in school.GRADES:
            spec = grade_spec(grade)
            code = spec.pop('code')
            programme, created = Programme.objects.get_or_create(
                institution=institution, code=code, defaults={'name': spec['name']})
            # Fees are facts from the fee schedule: always re-applied when they
            # are still unset, and on ``update``.
            self._apply(programme, spec, created)
            programmes[programme.full_code] = programme

            rows = school.subjects_for(grade)
            for order, (subject_code, group, note) in enumerate(rows, 1):
                module = modules[subject_code]
                offering, made = ProgrammeModule.objects.get_or_create(
                    programme=programme, code=subject_code, defaults={'module': module})
                self._apply(offering, {
                    'module': module, 'order': order, 'subject_group': group,
                    'description': note or module.description,
                }, made)
                if made or self.update:
                    offering.price_per_month = self.price
                    offering.save(update_fields=['price_per_month'])
                offerings.append(offering)

            Cohort.objects.get_or_create(
                programme=programme, code=str(self.year),
                defaults={'name': f'{programme.display_name} · {self.year}',
                          'start_date': self._date(*school.TERMS[0][1]),
                          'end_date': self._date(*school.TERMS[-1][2])})
            self.log(f'  {programme.full_code:9} {programme.display_name:9} {len(rows):>2} subjects · '
                     f'R{programme.monthly_fee:,.0f}/month · levy R{programme.annual_levy:,.0f}'
                     f'{"" if created else "   (already there)"}')
        return programmes, offerings

    # -- calendar -------------------------------------------------------------
    def _date(self, month, day):
        return date(self.year, month, day)

    def _at(self, month, day, hour=8):
        return timezone.make_aware(datetime(self.year, month, day, hour, 0))

    def _event(self, calendar, title, kind, when, *, end=None, programme=None,
               description='', published=True, provisional=False):
        event, created = CalendarEvent.objects.get_or_create(
            calendar=calendar, kind=kind, title=title, programme=programme,
            programme_module=None, defaults={'start': when})
        self._apply(event, {
            'start': when, 'end': end, 'all_day': True,
            'is_published': published or self.publish,
            'description': description + (PROVISIONAL if provisional else ''),
        }, created)
        return created

    def seed_calendar(self, institution):
        calendar, _ = AcademicCalendar.objects.get_or_create(
            institution=institution, year=self.year,
            defaults={'name': f'United Church School {self.year}',
                      'description': f'The {self.year} school year at United Church School: term '
                                     'dates, holidays, fee deadlines and examinations.'})
        made = 0

        # Terms, from the prospectus — published.
        for index, (term, (m1, d1), (m2, d2)) in enumerate(school.TERMS):
            made += self._event(calendar, f'{term} begins', CalendarEvent.KIND_ORIENTATION,
                                self._at(m1, d1), description=f'First day of {term}.')
            made += self._event(calendar, f'{term} ends', CalendarEvent.KIND_OTHER,
                                self._at(m2, d2), description=f'Last day of {term}.')
            if index + 1 < len(school.TERMS):
                start = self._date(m2, d2) + timedelta(days=1)
                nxt = school.TERMS[index + 1][1]
                finish = self._date(*nxt) - timedelta(days=1)
                made += self._event(
                    calendar, f'School holidays after {term}', CalendarEvent.KIND_HOLIDAY,
                    timezone.make_aware(datetime.combine(start, datetime.min.time())),
                    end=timezone.make_aware(datetime.combine(finish, datetime.min.time())),
                    description='School closed.')

        # Fee deadlines (prospectus "Fees 2026").
        for title, (month, day), note in school.FEE_DATES:
            made += self._event(calendar, title, CalendarEvent.KIND_DEADLINE, self._at(month, day),
                                description=note)

        # Public holidays.
        if self.holidays:
            for when, name in public_holidays(self.year):
                made += self._event(calendar, name, CalendarEvent.KIND_HOLIDAY,
                                    self._at(when.month, when.day),
                                    description='South African public holiday — school closed.')

        # Examination windows per grade (template, unpublished).
        for programme in institution.programmes.filter(is_active=True).order_by('grade'):
            grade = programme.grade or 0
            if grade < 4:
                continue                       # Foundation Phase: continuous assessment
            windows = ['mid-year', 'prelim', 'nsc'] if grade == 12 else ['mid-year', 'final']
            for key in windows:
                title, kind, (month, day), span, note = EXAM_WINDOWS[key]
                start = self._at(month, day)
                made += self._event(calendar, title, kind, start, programme=programme,
                                    end=start + timedelta(days=span - 1), description=note,
                                    published=False, provisional=True)
        self.log(f'  calendar     {calendar.events.count():>3} event(s) on the {self.year} '
                 f'calendar ({made} new)')
        return made

    # -- the whole thing --------------------------------------------------
    def run(self):
        institution = self.seed_institution()
        modules = self.seed_modules()
        programmes, offerings = self.seed_programmes(institution, modules)
        events = self.seed_calendar(institution) if self.calendar else 0
        return {
            'institutions': {institution.code: institution},
            'institution': institution,
            'modules': modules,
            'programmes': programmes,
            'offerings': offerings,
            'events_created': events,
            'events_total': (CalendarEvent.objects.filter(calendar__year=self.year).count()
                             if self.calendar else 0),
            'year': self.year,
            'price': self.price,
            'published': self.publish,
        }


def seed(**kwargs):
    """Build the spine. Keyword arguments are :class:`SpineSeeder`'s."""
    return SpineSeeder(**kwargs).run()


# --------------------------------------------------------------------------
# Putting people on the spine
# --------------------------------------------------------------------------
def allocate_students(students, allocation=STUDENT_ALLOCATION):
    """Spread ``students`` across the grades per :data:`STUDENT_ALLOCATION`.

    Returns ``[(person, programme), ...]`` covering every student exactly once.
    Counts are apportioned by largest remainder, so the shares come out whole and
    still add up to the number of students passed in. Deterministic.
    """
    total = len(students)
    if not total:
        return []

    programmes = {}
    for institution_code, programme_code, _share in allocation:
        key = f'{institution_code}-{programme_code}'
        programme = Programme.objects.filter(institution__code=institution_code,
                                             code=programme_code).first()
        if programme is not None:
            programmes[key] = programme

    live = [(f'{i}-{p}', share) for i, p, share in allocation if f'{i}-{p}' in programmes]
    weight = sum(share for _key, share in live) or 1
    exact = [(key, total * share / weight) for key, share in live]
    counts = {key: int(value) for key, value in exact}
    for key, value in sorted(exact, key=lambda kv: kv[1] - int(kv[1]), reverse=True):
        if sum(counts.values()) >= total:
            break
        counts[key] += 1

    pairs, index = [], 0
    for key, count in counts.items():
        for person in students[index:index + count]:
            pairs.append((person, programmes[key]))
        index += count
    return pairs


def default_subjects(programme):
    """The offerings a learner in ``programme`` takes by default: every
    compulsory subject plus, in Grade 10 – 12, the first options of each choice
    group (one FAL, Mathematics, the first three electives)."""
    offerings = list(programme.modules.filter(is_active=True).order_by('order', 'id'))
    chosen = [o for o in offerings if not o.subject_group]
    for key, (_label, pick) in school.SUBJECT_GROUPS.items():
        chosen += [o for o in offerings if o.subject_group == key][:pick]
    return chosen


def enrol_student(person, programme, *, cohort=None, activate=True, months=6, offerings=None):
    """Register ``person`` in ``programme`` (a grade) and its subjects.

    ``offerings`` defaults to :func:`default_subjects`. ``activate`` marks them
    paid (so a demo learner can open the material); pass ``False`` to leave them
    LOCKED, which is how a real registration starts until fees are paid.
    Returns ``(programme_enrolment, [module_enrolments])``.
    """
    if cohort is None:
        cohort = (programme.cohorts.filter(is_active=True, code=str(school.YEAR)).first()
                  or programme.cohorts.filter(is_active=True).order_by('-start_date', 'code').first())
    enrolment, _ = ProgrammeEnrolment.objects.get_or_create(
        person=person, programme=programme, defaults={'cohort': cohort})
    if cohort is not None and enrolment.cohort_id is None:
        enrolment.cohort = cohort
        enrolment.save(update_fields=['cohort', 'updated_at'])

    modules = []
    for offering in (offerings if offerings is not None else default_subjects(programme)):
        module_enrolment, created = ModuleEnrolment.objects.get_or_create(
            person=person, programme_module=offering,
            defaults={'price_at_enrolment': offering.price_per_month,
                      'started_at': timezone.now()})
        if created and activate:
            module_enrolment.activate(months=months)
        modules.append(module_enrolment)
    if not person.enrolled_class:
        person.enrolled_class = programme.display_name[:100]
        person.save(update_fields=['enrolled_class'])
    return enrolment, modules


def assign_educator(person, offerings):
    """Put ``person`` down as a teacher on each of ``offerings``."""
    for offering in offerings:
        offering.educators.add(person)
    return len(offerings)
