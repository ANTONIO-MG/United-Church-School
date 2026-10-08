"""
core/academic_spine.py  —  United Church School's academic spine, built.

The school, its twelve grades, the CAPS subjects offered in each grade, each
grade's 2026 fee schedule, the year's class per grade and the school calendar.
The *facts* live in :mod:`core.school` (from www.ucs.org.za and the UCS
Application Form 2026); this module turns them into rows.
``.03_admin.py`` installs it as part of a fresh build and
``.04_demo_seed.py`` enrols its demo learners and teachers into what it created.

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
* **The school calendars for 2026 and 2027** (from :mod:`core.school_calendar`)
  — terms (UCS prospectus dates for 2026, the gazetted DBE/GDE calendar for
  2027), school and public holidays (incl. once-off ones), fee deadlines,
  report days, the NSC, preliminary, mid-year and November examinations, the
  Foundation Phase assessment weeks and the GDE admissions windows. Each grade
  date is written on its grade's programme, so a learner sees whole-school
  dates plus their own grade's (see :mod:`apps.livesessions.academic`).

⚠️  **Estimated dates are written unpublished.** Every event in
:mod:`core.school_calendar` is tagged official (published by the school, the
DBE or the GDE) or estimate. Estimates are unpublished (staff-only) unless
``publish=True`` and say so in their description; confirm them in the Django
admin (Learning → Academic calendars) once the real timetable is out. A re-seed
refreshes rows that are still unconfirmed estimates and leaves edited ones alone.

Using it
--------
    from core import academic_spine

    result = academic_spine.seed()                       # everything, school year
    result = academic_spine.seed(year=2027)              # 2027's calendar + class only
    result = academic_spine.seed(calendar_years=[2026, 2027, 2028])  # these calendars
    result = academic_spine.seed(calendar=False)         # spine only, fast

    # putting people on it (see .04_demo_seed.py)
    for person, programme in academic_spine.allocate_students(students):
        academic_spine.enrol_student(person, programme)

Seeding is idempotent and non-destructive: it creates what is missing and leaves
existing rows alone. With ``update=False`` (the default) it only fills blanks, so
edits made in the admin survive a re-run; ``update=True`` re-applies the facts
(e.g. after editing a fee in :mod:`core.school`).
"""
from datetime import date, datetime
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
from core import school, school_calendar

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


# The school calendar's facts — terms, holidays, examinations and every other
# dated event, each tagged with the grades it applies to — live in
# :mod:`core.school_calendar` (2026 and 2027, with sources). Kept here as names
# for older imports.
FIXED_HOLIDAYS = school_calendar.FIXED_HOLIDAYS

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
    """Easter Sunday — see :func:`core.school_calendar.easter_sunday`."""
    return school_calendar.easter_sunday(year)


def public_holidays(year):
    """``[(date, name)]`` for the year, Sunday roll-over and once-off holidays
    applied — see :func:`core.school_calendar.public_holidays`."""
    return school_calendar.public_holidays(year)


def crest_png():
    """The school crest as PNG bytes (``None`` if the static file is missing)."""
    try:
        return CREST.read_bytes()
    except OSError:
        return None


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------
PROVISIONAL = ('\n\nEstimated date — not yet published by the school, the DBE or the GDE. '
               'Confirm against the official timetable and correct it here.')
#: Descriptions that mark a row as still the seed's own estimate (this text, or
#: the template wording older seeds wrote) — such rows are refreshed on re-seed.
_SEED_MARKERS = ('Estimated date — not yet published', 'Template date — the school has not')


class SpineSeeder:
    """Builds the spine. See :func:`seed` for the usual way in."""

    def __init__(self, *, year=None, price=DEFAULT_PRICE, update=False, logos=True,
                 refresh_logos=False, calendar=True, holidays=True, publish=False,
                 verbose=True, indent='  ', calendar_years=None):
        self.year = year or school.YEAR
        # Which school calendars to build: an explicit list, else the given
        # ``year`` alone, else every year core.school_calendar knows (2026, 2027).
        if calendar_years:
            self.calendar_years = sorted(set(int(y) for y in calendar_years))
        elif year:
            self.calendar_years = [int(year)]
        else:
            self.calendar_years = sorted(school_calendar.YEARS)
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

    def _at(self, month, day, hour=8, year=None):
        return timezone.make_aware(datetime(year or self.year, month, day, hour, 0))

    def _day(self, when):
        """A ``date`` → an aware datetime at 08:00 (all-day dates sort sensibly)."""
        return self._at(when.month, when.day, year=when.year)

    def _event(self, calendar, title, kind, when, *, end=None, programme=None,
               description='', published=True, provisional=False):
        event, created = CalendarEvent.objects.get_or_create(
            calendar=calendar, kind=kind, title=title, programme=programme,
            programme_module=None, defaults={'start': when})
        fields = {
            'start': when, 'end': end, 'all_day': True,
            'is_published': published or self.publish,
            'description': description + (PROVISIONAL if provisional else ''),
        }
        # A row that is still the seed's own unpublished estimate (nobody has
        # confirmed it in the admin) follows the facts; anything else keeps its edits.
        seed_owned = (not created and not event.is_published
                      and any(m in (event.description or '') for m in _SEED_MARKERS))
        if seed_owned and not self.update:
            self.update = True
            try:
                self._apply(event, fields, created)
            finally:
                self.update = False
        else:
            self._apply(event, fields, created)
        return created

    def seed_calendar(self, institution, years=None):
        """Build the school calendar(s) from :mod:`core.school_calendar`.

        One :class:`AcademicCalendar` per year (default ``self.calendar_years`` —
        2026 and 2027). Whole-school dates are written once (no programme);
        a grade date is written once per grade it applies to, on that grade's
        :class:`Programme`, so each learner's calendar shows only their grade's.
        Official dates are published; estimates are not (unless ``publish``).
        Returns the number of events created.
        """
        made = 0
        programmes = {p.grade: p for p in
                      institution.programmes.filter(is_active=True, grade__isnull=False)}
        for year in (years or self.calendar_years):
            made += self._seed_calendar_year(institution, int(year), programmes)
        return made

    def _seed_calendar_year(self, institution, year, programmes):
        known = year in school_calendar.YEARS
        calendar, _ = AcademicCalendar.objects.get_or_create(
            institution=institution, year=year,
            defaults={'name': f'United Church School {year}',
                      'description': f'The {year} school year at United Church School: terms, '
                                     'holidays, fee deadlines, examinations and admissions '
                                     '(per grade).' + ('' if known else
                                     ' Outline only — no published calendar for this year yet.')})
        made = 0
        for item in school_calendar.events_for(year):
            if item.kind == school_calendar.HOLIDAY and not self.holidays \
                    and not item.title.startswith('School holidays'):
                continue                          # public / special holidays switched off
            start = self._day(item.start)
            end = self._day(item.end) if item.end else None
            description = item.description
            if item.source and item.official:
                description = f'{description}\n\nSource: {item.source}.'.strip()
            targets = ([None] if item.grades is None
                       else [programmes[g] for g in item.grades if g in programmes])
            for programme in targets:
                made += self._event(calendar, item.title, item.kind, start, end=end,
                                    programme=programme, description=description,
                                    published=item.official, provisional=not item.official)
        self.log(f'  calendar     {calendar.events.count():>3} event(s) on the {year} '
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
            'events_total': (CalendarEvent.objects
                             .filter(calendar__year__in=self.calendar_years).count()
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
