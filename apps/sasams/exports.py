"""SA-SAMS export for the Department (GDE): learner register, parents, mark
schedules, attendance, and a data-quality report.

SA-SAMS (the DBE's School Administration and Management System) has no public
import specification, so the layouts below are the closest faithful layout to
what is published (see ``SOURCES`` and the workbook's *Read me* sheet). Every
sheet is described by ONE column-spec list — ``LEARNER_COLUMNS``,
``GUARDIAN_COLUMNS``, ``MARK_COLUMNS``, ``ATTENDANCE_COLUMNS`` — of
``(header, getter)`` pairs. To match a district template exactly, rename the
headers or reorder the tuples there; nothing else needs to change.

Entry points:

* :func:`collect` — the learners in a year (optionally one grade), with their
  application, class and contact details.
* :func:`build_tables` — ``{sheet name: (headers, rows)}`` for every sheet.
* :func:`build_workbook` / :func:`workbook_bytes` — the XLSX.
* :func:`csv_zip_bytes` — one CSV per sheet, zipped (SA-SAMS's import wizard
  reads Excel; CSV is for districts / LURITS tools that ask for it).
* :func:`data_quality` — what the office should fix before submitting.
"""
import csv
import datetime
import io
import re
import zipfile
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field

from django.conf import settings
from django.db.models import Count
from django.utils import timezone

# ---------------------------------------------------------------------------
# Sources consulted (shown on the Read me sheet)
# ---------------------------------------------------------------------------
SOURCES = [
    ('d6 School Communicator — learner import template (SA-SAMS/LURITS-compatible columns: '
     'Full names, Surname, Grade, Register class, Gender, Birthdate, ID number, Passport number, '
     'Ethnic group, LURITS number, Religion, Nationality, Home/Tuition language, Dexterity, '
     'Admission date; dates YYYY-MM-DD)',
     'https://help.d6.co.za/portal/en/kb/articles/how-to-import-learners-using-the-excel-template-20-4-2026'),
    ('DataFirst (UCT) — LURITS 2024 data dictionary (EmisCode, IDNo, AccessionNo, BirthDate, '
     'FirstName, Surname, Grade, ClassCode, Gender, Race)',
     'https://www.datafirst.uct.ac.za/Dataportal/index.php/catalog/1065/data-dictionary/F4'),
    ('National Protocol for Assessment / NSC recording & reporting — 7-point scale of achievement',
     'https://www.acts.co.za/south-african-schools-act/nsc_15_recording_and_reporting.php'),
    ('Stats SA population-group codes (1 Black African, 2 Coloured, 3 Indian/Asian, 4 White, '
     '5 Other)', 'https://microdata.worldbank.org/catalog/2773/variable/F2/V308?name=race'),
    ('d6 — learner (admission) numbers; learner ID numbers are mandatory on LURITS and SA-SAMS',
     'https://help.d6.co.za/portal/en/kb/schoolmanagement/reports/learners/learner-numbers'),
]

ASSUMPTIONS = [
    'The DBE does not publish SA-SAMS\'s import file specification. Column headers follow the '
    'SA-SAMS/LURITS-compatible learner import used by accredited school software (d6) and the '
    'LURITS data dictionary. Rename headers in apps/sasams/exports.py (LEARNER_COLUMNS etc.) to '
    'match a district template exactly.',
    'Coded fields are given as the description SA-SAMS shows in its pick lists (e.g. "isiZulu", '
    '"African"), plus a numeric population-group code (Stats SA 1-5) in its own column, so the '
    'office can map either way.',
    'Gender is exported as M / F. A learner recorded as "other" is left blank and flagged.',
    'Admission number = the school\'s own learner number (SA-SAMS "admission"/"accession" number). '
    'Blank values are left blank and listed on the Data quality sheet.',
    'Register class: a class coded with the year only (e.g. "2026") means the grade has one class; '
    'it is exported as "<grade>A" (e.g. "5A"). Named classes (e.g. "10B") are exported as-is.',
    'Language of learning and teaching (LoLT) is English for every learner at UCS.',
    'Admission date = the first day the learner was admitted to UCS on the platform (earliest '
    'admitted application decision, else the grade enrolment date).',
    'Mark schedules carry only PUBLISHED term results unless "include drafts" was chosen. Term % '
    'is the CAPS-weighted term mark (SBA + exam where an exam applies); level is the CAPS 1-7 '
    'achievement level. Subject codes are UCS codes (e.g. MATH, ENG-HL); SA-SAMS subject codes can '
    'be set in SUBJECT_CODE_MAP.',
    'Attendance counts come from the daily register for the term\'s dates. "Days present" includes '
    'days marked late; excused absences are counted separately from (unexcused) absences.',
    'Learners in the year = active learners in each grade\'s class for that year, plus learners '
    'with an admitted application for that year and grade.',
]

#: UCS subject code -> SA-SAMS subject code. Empty = export the UCS code.
SUBJECT_CODE_MAP = {}

LOLT = 'English'

# ---------------------------------------------------------------------------
# Code tables
# ---------------------------------------------------------------------------
GENDER_CODES = {'male': 'M', 'female': 'F', 'm': 'M', 'f': 'F'}

#: application race value -> (SA-SAMS description, Stats SA code)
POPULATION_GROUPS = {
    'african': ('African', 1),
    'black': ('African', 1),
    'coloured': ('Coloured', 2),
    'indian': ('Indian', 3),
    'asian': ('Indian', 3),
    'white': ('White', 4),
    'other': ('Other', 5),
}

#: The official languages (and SASL) as SA-SAMS lists them, by lower-case alias.
LANGUAGES = OrderedDict([
    ('Afrikaans', ('afrikaans', 'afr')),
    ('English', ('english', 'eng')),
    ('isiNdebele', ('isindebele', 'ndebele', 'south ndebele')),
    ('isiXhosa', ('isixhosa', 'xhosa')),
    ('isiZulu', ('isizulu', 'zulu')),
    ('Sepedi', ('sepedi', 'pedi', 'northern sotho', 'sesotho sa leboa')),
    ('Sesotho', ('sesotho', 'sotho', 'southern sotho', 'south sotho')),
    ('Setswana', ('setswana', 'tswana')),
    ('siSwati', ('siswati', 'swati', 'swazi')),
    ('Tshivenda', ('tshivenda', 'venda', 'tshivenḓa')),
    ('Xitsonga', ('xitsonga', 'tsonga', 'shangaan')),
    ('South African Sign Language', ('south african sign language', 'sasl', 'sign language')),
])
_LANG_ALIASES = {alias: name for name, aliases in LANGUAGES.items() for alias in aliases}
OTHER_LANGUAGE = 'Other'

DEXTERITY = {'right': 'Right', 'left': 'Left', 'both': 'Ambidextrous'}

ROLE_LABELS = {'father': 'Father', 'mother': 'Mother', 'guardian': 'Guardian'}


def gender_code(value):
    return GENDER_CODES.get((value or '').strip().lower(), '')


def population_group(value):
    """``(description, code)`` or ``('', '')``."""
    return POPULATION_GROUPS.get((value or '').strip().lower(), ('', ''))


def language_name(value):
    """Official spelling of a home language; ``'Other'`` for a non-SA language;
    ``''`` when blank."""
    raw = (value or '').strip()
    if not raw:
        return ''
    return _LANG_ALIASES.get(raw.lower(), OTHER_LANGUAGE)


def subject_code(module):
    return SUBJECT_CODE_MAP.get(module.code, module.code)


def _date(value):
    if value is None or value == '':
        return ''
    if isinstance(value, datetime.datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        value = value.date()
    return value.isoformat()


def initials(first_names):
    return ''.join(part[0].upper() for part in (first_names or '').split() if part)


def split_full_name(full_name):
    """``('Thandi Grace', 'Mokoena')`` from ``'Thandi Grace Mokoena'``."""
    parts = (full_name or '').split()
    if len(parts) < 2:
        return (full_name or '').strip(), ''
    return ' '.join(parts[:-1]), parts[-1]


# ---------------------------------------------------------------------------
# SA ID number validation
# ---------------------------------------------------------------------------
def luhn_ok(number):
    digits = [int(d) for d in number]
    total = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def id_birth_date(number, hint=None):
    """Date of birth encoded in a 13-digit SA ID (YYMMDD...), or None. ``hint``
    (the recorded date of birth) resolves the century; otherwise the most recent
    century not in the future is used."""
    try:
        yy, mm, dd = int(number[0:2]), int(number[2:4]), int(number[4:6])
    except (TypeError, ValueError):
        return None
    centuries = [2000, 1900]
    if hint is not None:
        centuries.sort(key=lambda c: abs((c + yy) - hint.year))
    today = timezone.localdate()
    for century in centuries:
        try:
            day = datetime.date(century + yy, mm, dd)
        except ValueError:
            return None
        if hint is not None or day <= today:
            return day
    return None


def check_sa_id(number, date_of_birth=None, gender=None, is_citizen=None):
    """Problems with a South African ID number (``[]`` when it is valid).

    13 digits ``YYMMDD SSSS C A Z``: a real birth date (matching the recorded
    one), gender digits (0000-4999 female, 5000-9999 male), citizenship digit
    (0 citizen, 1 permanent resident) and the Luhn check digit.
    """
    raw = re.sub(r'\s+', '', number or '')
    if not raw:
        return []
    if not raw.isdigit() or len(raw) != 13:
        return [f'ID number "{number}" is not 13 digits']
    problems = []
    born = id_birth_date(raw, hint=date_of_birth)
    if born is None:
        problems.append(f'ID number "{raw}" does not start with a valid date of birth (YYMMDD)')
    elif date_of_birth is not None and born != date_of_birth:
        problems.append(f'ID number date of birth {born:%Y-%m-%d} does not match the recorded '
                        f'date of birth {date_of_birth:%Y-%m-%d}')
    sex = gender_code(gender)
    if sex:
        id_sex = 'M' if int(raw[6:10]) >= 5000 else 'F'
        if id_sex != sex:
            problems.append(f'ID number gender digits say {id_sex} but the learner is recorded as {sex}')
    if raw[10] not in '01':
        problems.append(f'ID number citizenship digit is {raw[10]} (must be 0 or 1)')
    if not luhn_ok(raw):
        problems.append(f'ID number "{raw}" fails the check-digit (Luhn) test')
    return problems


# ---------------------------------------------------------------------------
# Who is in the year
# ---------------------------------------------------------------------------
@dataclass
class LearnerRecord:
    person: object
    programme: object
    cohort: object = None
    application: object = None
    guardians: list = field(default_factory=list)
    admission_date: object = None

    @property
    def grade(self):
        return self.programme.grade

    @property
    def contact(self):
        return getattr(self.person, 'contact', None)

    @property
    def register_class(self):
        cohort = self.cohort
        if cohort is None or not cohort.code or re.fullmatch(r'\d{4}', cohort.code):
            return f'{self.grade}A' if self.grade else ''
        return cohort.code

    def app(self, attr, default=''):
        if self.application is None:
            return default
        value = getattr(self.application, attr, default)
        return default if value is None else value

    @property
    def gender(self):
        return self.app('gender') or (self.person.gender or '')

    @property
    def is_citizen(self):
        return bool(self.app('is_south_african', True))


def grades():
    from apps.learning.models import Programme
    return list(Programme.objects.filter(is_active=True, institution__code='UCS',
                                         grade__isnull=False).order_by('grade'))


def collect(year, grade=None):
    """``[LearnerRecord]`` for ``year`` (optionally only grade number ``grade``),
    ordered by grade, class, surname, first names."""
    from apps.accounts.models import Person
    from apps.admissions.models import Application
    from apps.admissions.promotion import learners_in
    from apps.learning.models import ProgrammeEnrolment

    year = int(year)
    programmes = [p for p in grades() if grade in (None, '', p.grade) or str(grade) == str(p.grade)]
    records, seen = [], set()
    for programme in programmes:
        ids = set(learners_in(programme, year).filter(user_type='student').values_list('pk', flat=True))
        ids |= set(Application.objects.filter(year=year, programme=programme,
                                              status=Application.STATUS_ADMITTED,
                                              person__user_type='student')
                   .values_list('person_id', flat=True))
        ids -= seen
        seen |= ids
        people = (Person.objects.filter(pk__in=ids).select_related('user', 'contact')
                  .order_by('last_name', 'first_name'))
        for person in people:
            enrolment = (ProgrammeEnrolment.objects.filter(person=person, programme=programme)
                         .select_related('cohort').first())
            apps = list(Application.objects.filter(person=person).order_by('-year'))
            application = (next((a for a in apps if a.year == year), None)
                           or next((a for a in apps if a.year < year), None)
                           or (apps[-1] if apps else None))
            admitted = sorted(a.decided_at for a in apps
                              if a.status == Application.STATUS_ADMITTED and a.decided_at)
            if admitted:
                admission_date = admitted[0]
            else:
                first = (ProgrammeEnrolment.objects.filter(person=person)
                         .order_by('created_at').values_list('created_at', flat=True).first())
                admission_date = first
            guardians = list(application.guardians.all()) if application else []
            records.append(LearnerRecord(person=person, programme=programme,
                                         cohort=enrolment.cohort if enrolment else None,
                                         application=application, guardians=guardians,
                                         admission_date=admission_date))
    records.sort(key=lambda r: (r.grade or 0, r.register_class, (r.person.last_name or '').lower(),
                                (r.person.first_name or '').lower()))
    return records


# ---------------------------------------------------------------------------
# Column specs — ONE list per sheet. Edit headers / order here.
# ---------------------------------------------------------------------------
def _emis(_r=None):
    return getattr(settings, 'SCHOOL_EMIS_NUMBER', '') or ''


def _id_number(r):
    return re.sub(r'\s+', '', r.app('id_number'))


def _permit(r):
    return r.app('permit_number') or r.app('study_permit_number')


def _citizenship(r):
    if r.application is None:
        return ''
    if r.is_citizen:
        return 'South African'
    return 'Permanent resident' if r.app('permanent_residency', False) else 'Non-South African'


def _nationality(r):
    if r.application is None:
        return ''
    if r.is_citizen:
        return 'South Africa'
    return r.app('document_country')


def _contact(r, attr):
    contact = r.contact
    return getattr(contact, attr, '') if contact else ''


def _fee_payer(r, g):
    payer = r.app('fee_payer')
    return 'Y' if payer == g.role or (payer == 'both' and g.role in ('father', 'mother')) else 'N'


def _address(r):
    return ' '.join((r.app('physical_address') or '').split())


LEARNER_COLUMNS = [
    ('EMIS Number', _emis),
    ('Admission Number', lambda r: r.person.admission_number),
    ('LURITS Number', lambda r: r.person.lurits_number),
    ('Learner Surname', lambda r: r.person.last_name),
    ('Learner Full Names', lambda r: r.person.first_name),
    ('Learner Initials', lambda r: initials(r.person.first_name)),
    ('Learner Grade', lambda r: r.grade),
    ('Learner Register Class', lambda r: r.register_class),
    ('Learner Gender', lambda r: gender_code(r.gender)),
    ('Learner Birthdate', lambda r: _date(r.person.date_of_birth)),
    ('Learner ID Number', _id_number),
    ('Learner Passport Number', lambda r: r.app('passport_number')),
    ('Learner Permit Number', _permit),
    ('Citizenship', _citizenship),
    ('Nationality', _nationality),
    ('Learner Ethnic Group', lambda r: population_group(r.app('race'))[0]),
    ('Population Group Code', lambda r: population_group(r.app('race'))[1]),
    ('Learner Home Language', lambda r: language_name(r.app('home_language'))),
    ('Learner Tuition Language', lambda r: LOLT),
    ('Religion', lambda r: r.app('religion')),
    ('Learner Dexterity', lambda r: DEXTERITY.get(r.app('writing_hand'), '')),
    ('Learner Admission Date', lambda r: _date(r.admission_date)),
    ('Previous School', lambda r: r.app('previous_school')),
    ('Cell Number', lambda r: _contact(r, 'primary_phone') or r.person.phone),
    ('Residential Address', _address),
    ('Suburb', lambda r: _contact(r, 'suburb')),
    ('City / Town', lambda r: _contact(r, 'city')),
    ('Province', lambda r: _contact(r, 'province')),
    ('Medical Aid', lambda r: r.app('medical_aid_name')),
    ('Medical Aid Number', lambda r: r.app('medical_aid_number')),
]

# Guardian rows: (record, guardian)
GUARDIAN_COLUMNS = [
    ('EMIS Number', lambda r, g: _emis()),
    ('Learner Admission Number', lambda r, g: r.person.admission_number),
    ('Learner ID Number', lambda r, g: _id_number(r)),
    ('Learner Surname', lambda r, g: r.person.last_name),
    ('Learner Full Names', lambda r, g: r.person.first_name),
    ('Learner Grade', lambda r, g: r.grade),
    ('Relationship', lambda r, g: ROLE_LABELS.get(g.role, g.role)),
    ('Title', lambda r, g: g.title),
    ('Parent Surname', lambda r, g: split_full_name(g.full_name)[1]),
    ('Parent Full Names', lambda r, g: split_full_name(g.full_name)[0]),
    ('Parent Initials', lambda r, g: initials(split_full_name(g.full_name)[0])),
    ('Parent ID / Passport Number', lambda r, g: re.sub(r'\s+', '', g.id_number or '')),
    ('Cell Number', lambda r, g: g.cell_phone),
    ('Home Tel', lambda r, g: g.home_phone),
    ('Work Tel', lambda r, g: g.work_phone),
    ('E-mail', lambda r, g: g.email),
    ('Residential Address', lambda r, g: ' '.join((g.residential_address or '').split())),
    ('Occupation', lambda r, g: g.occupation),
    ('Employer', lambda r, g: g.employer),
    ('Fee Payer', lambda r, g: _fee_payer(r, g)),
]

# Long-format marks: (record, term_result)
MARK_COLUMNS = [
    ('EMIS Number', lambda r, t: _emis()),
    ('Year', lambda r, t: t.year),
    ('Term', lambda r, t: t.term),
    ('Grade', lambda r, t: r.grade),
    ('Register Class', lambda r, t: r.register_class),
    ('Admission Number', lambda r, t: r.person.admission_number),
    ('LURITS Number', lambda r, t: r.person.lurits_number),
    ('Learner Surname', lambda r, t: r.person.last_name),
    ('Learner Full Names', lambda r, t: r.person.first_name),
    ('Subject Code', lambda r, t: subject_code(t.module)),
    ('Subject', lambda r, t: t.module.display_name),
    ('SBA %', lambda r, t: _num(t.sba_pct if t.sba_pct is not None else t.auto_pct)),
    ('Exam %', lambda r, t: _num(t.exam_pct)),
    ('Term Mark %', lambda r, t: _num(t.term_pct)),
    ('Achievement Level', lambda r, t: t.level or ''),
    ('Level Descriptor', lambda r, t: LEVEL_DESCRIPTORS.get(t.level, '')),
    ('Status', lambda r, t: t.status),
]

# Attendance: (record, counts)
ATTENDANCE_COLUMNS = [
    ('EMIS Number', lambda r, c: _emis()),
    ('Year', lambda r, c: c['year']),
    ('Term', lambda r, c: c['term']),
    ('Grade', lambda r, c: r.grade),
    ('Register Class', lambda r, c: r.register_class),
    ('Admission Number', lambda r, c: r.person.admission_number),
    ('LURITS Number', lambda r, c: r.person.lurits_number),
    ('Learner Surname', lambda r, c: r.person.last_name),
    ('Learner Full Names', lambda r, c: r.person.first_name),
    ('School Days Recorded', lambda r, c: c['total']),
    ('Days Present', lambda r, c: c['present'] + c['late']),
    ('Days Late', lambda r, c: c['late']),
    ('Days Absent (Unexcused)', lambda r, c: c['absent']),
    ('Days Absent (Excused)', lambda r, c: c['excused']),
    ('Total Days Absent', lambda r, c: c['absent'] + c['excused']),
    ('Attendance %', lambda r, c: c['pct']),
]

DATA_QUALITY_COLUMNS = ['Grade', 'Register Class', 'Admission Number', 'Learner Surname',
                        'Learner Full Names', 'Field', 'Severity', 'Problem']

LEVEL_DESCRIPTORS = {7: 'Outstanding achievement', 6: 'Meritorious achievement',
                     5: 'Substantial achievement', 4: 'Adequate achievement',
                     3: 'Moderate achievement', 2: 'Elementary achievement', 1: 'Not achieved'}
LEVEL_BANDS = {7: '80-100', 6: '70-79', 5: '60-69', 4: '50-59', 3: '40-49', 2: '30-39', 1: '0-29'}


def _num(value):
    if value is None or value == '':
        return ''
    number = float(value)
    return int(number) if number.is_integer() else round(number, 1)


def _clean(value):
    return '' if value is None else value


# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------
ERROR, WARNING = 'Error', 'Warning'


def data_quality(records):
    """``[dict]`` — one row per problem: grade, class, admission number,
    surname, first names, field, severity, problem."""
    issues = []

    def flag(r, fieldname, problem, severity=ERROR):
        issues.append({'Grade': r.grade, 'Register Class': r.register_class,
                       'Admission Number': r.person.admission_number,
                       'Learner Surname': r.person.last_name,
                       'Learner Full Names': r.person.first_name,
                       'Field': fieldname, 'Severity': severity, 'Problem': problem,
                       # template-friendly aliases
                       'person_id': r.person.pk, 'name': f'{r.person.last_name}, {r.person.first_name}'.strip(', '),
                       'register_class': r.register_class, 'admission': r.person.admission_number,
                       'is_error': severity == ERROR})

    admission_seen, lurits_seen = defaultdict(list), defaultdict(list)
    for r in records:
        p = r.person
        if not (p.last_name or '').strip():
            flag(r, 'Learner Surname', 'Surname missing')
        if not (p.first_name or '').strip():
            flag(r, 'Learner Full Names', 'First names missing')
        if not (p.admission_number or '').strip():
            flag(r, 'Admission Number', 'Admission number missing')
        else:
            admission_seen[p.admission_number.strip().lower()].append(r)
        if not (p.lurits_number or '').strip():
            flag(r, 'LURITS Number', 'LURITS number missing (new learners get one once captured '
                 'on SA-SAMS)', WARNING)
        else:
            lurits = p.lurits_number.strip()
            lurits_seen[lurits].append(r)
            if not lurits.isdigit():
                flag(r, 'LURITS Number', f'LURITS number "{lurits}" should contain digits only',
                     WARNING)
        if p.date_of_birth is None:
            flag(r, 'Learner Birthdate', 'Date of birth missing')
        if not gender_code(r.gender):
            flag(r, 'Learner Gender', 'Gender missing or not M/F')
        if r.application is None:
            flag(r, 'Application', 'No application on record — ID, home language, population '
                 'group and parents cannot be exported')
            continue
        id_number = _id_number(r)
        if r.is_citizen or r.app('permanent_residency', False):
            if not id_number:
                flag(r, 'Learner ID Number', 'SA ID number missing (South African learner)')
            for problem in check_sa_id(id_number, p.date_of_birth, r.gender, r.is_citizen):
                flag(r, 'Learner ID Number', problem)
        else:
            if not (r.app('passport_number') or _permit(r) or id_number):
                flag(r, 'Learner Passport Number', 'Non-South African learner without a passport '
                     'or permit number')
            if not r.app('document_country'):
                flag(r, 'Nationality', 'Country of issue (nationality) missing', WARNING)
        language = r.app('home_language')
        if not language:
            flag(r, 'Learner Home Language', 'Home language missing')
        elif language_name(language) == OTHER_LANGUAGE:
            flag(r, 'Learner Home Language', f'"{language}" is not one of the SA official languages '
                 '— exported as "Other"', WARNING)
        if not population_group(r.app('race'))[0]:
            flag(r, 'Learner Ethnic Group', 'Population group (race) missing')
        if not r.guardians:
            flag(r, 'Parents', 'No parent / guardian recorded')
        elif not any((g.cell_phone or g.home_phone or g.work_phone) for g in r.guardians):
            flag(r, 'Parents', 'No parent / guardian phone number', WARNING)

    for value, rows in admission_seen.items():
        if len(rows) > 1:
            for r in rows:
                flag(r, 'Admission Number', f'Admission number "{r.person.admission_number}" is used '
                     f'by {len(rows)} learners')
    for value, rows in lurits_seen.items():
        if len(rows) > 1:
            for r in rows:
                flag(r, 'LURITS Number', f'LURITS number "{value}" is used by {len(rows)} learners')
    issues.sort(key=lambda i: (i['Grade'] or 0, i['Register Class'], i['Learner Surname'].lower(),
                               i['Severity'] != ERROR, i['Field']))
    return issues


def quality_summary(issues):
    """``[(field, problem kind, count)]`` — counts of each missing field."""
    counts = defaultdict(lambda: {'Error': 0, 'Warning': 0})
    for issue in issues:
        counts[issue['Field']][issue['Severity']] += 1
    return sorted(((f, c['Error'], c['Warning']) for f, c in counts.items()),
                  key=lambda row: (-row[1], -row[2], row[0]))


# ---------------------------------------------------------------------------
# Sheets
# ---------------------------------------------------------------------------
def _published_results(records, year, term, include_drafts):
    from apps.reports.models import TermResult
    users = [r.person.user_id for r in records if r.person.user_id]
    results = (TermResult.objects.filter(student_id__in=users, year=year, term=term)
               .select_related('module', 'module__module', 'module__programme'))
    if not include_drafts:
        results = results.filter(status=TermResult.STATUS_PUBLISHED)
    by_user = defaultdict(dict)
    for result in results:
        by_user[result.student_id][result.module_id] = result
    return by_user


def _attendance(records, year, term):
    from apps.attendance.models import AttendanceMark
    from apps.reports.terms import term_dates
    start, end = term_dates(year, term)
    rows = (AttendanceMark.objects.filter(learner__in=[r.person for r in records],
                                          register__date__gte=start, register__date__lte=end)
            .values('learner_id', 'status').annotate(n=Count('id')))
    counts = defaultdict(lambda: {s: 0 for s in ('present', 'absent', 'late', 'excused')})
    for row in rows:
        counts[row['learner_id']][row['status']] = row['n']
    out = {}
    for r in records:
        c = dict(counts[r.person.pk])
        c['total'] = sum(c.values())
        c['pct'] = round((c['present'] + c['late']) * 100 / c['total'], 1) if c['total'] else ''
        c['year'], c['term'], c['start'], c['end'] = year, term, start, end
        out[r.person.pk] = c
    return out


def marks_sheet_name(grade, term):
    return f'Marks Gr{int(grade):02d} T{term}'


def build_tables(year, term, grade=None, include_drafts=False, records=None):
    """``OrderedDict{sheet name: (headers, rows)}`` for every data sheet
    (Read me is added by :func:`build_workbook`)."""
    year, term = int(year), int(term)
    records = collect(year, grade) if records is None else records
    tables = OrderedDict()

    tables['Learners'] = ([h for h, _ in LEARNER_COLUMNS],
                          [[_clean(get(r)) for _, get in LEARNER_COLUMNS] for r in records])

    tables['Parents'] = ([h for h, _ in GUARDIAN_COLUMNS],
                         [[_clean(get(r, g)) for _, get in GUARDIAN_COLUMNS]
                          for r in records for g in r.guardians])

    results = _published_results(records, year, term, include_drafts)
    long_rows = []
    by_grade = OrderedDict()
    for r in records:
        by_grade.setdefault(r.programme, []).append(r)
    for programme, group in by_grade.items():
        subjects = list(programme.modules.filter(is_active=True).select_related('module')
                        .order_by('order', 'id'))
        headers = ['Admission Number', 'LURITS Number', 'Learner Surname', 'Learner Full Names',
                   'Register Class']
        for module in subjects:
            headers += [f'{subject_code(module)} %', f'{subject_code(module)} Level']
        rows = []
        for r in group:
            row = [r.person.admission_number, r.person.lurits_number, r.person.last_name,
                   r.person.first_name, r.register_class]
            mine = results.get(r.person.user_id, {})
            for module in subjects:
                result = mine.get(module.pk)
                row += ['', ''] if result is None else [_num(result.term_pct), result.level or '']
                if result is not None:
                    long_rows.append([_clean(get(r, result)) for _, get in MARK_COLUMNS])
            rows.append(row)
        tables[marks_sheet_name(programme.grade, term)] = (headers, rows)
    tables[f'Marks T{term} (list)'] = ([h for h, _ in MARK_COLUMNS], long_rows)

    attendance = _attendance(records, year, term)
    tables[f'Attendance T{term}'] = (
        [h for h, _ in ATTENDANCE_COLUMNS],
        [[_clean(get(r, attendance[r.person.pk])) for _, get in ATTENDANCE_COLUMNS] for r in records])

    issues = data_quality(records)
    tables['Data quality'] = (DATA_QUALITY_COLUMNS,
                              [[_clean(i[c]) for c in DATA_QUALITY_COLUMNS] for i in issues])
    return tables


def readme_rows(year, term, grade=None, include_drafts=False, tables=None):
    from core.branding import BRAND
    from apps.reports.terms import term_dates
    start, end = term_dates(year, term)
    rows = [
        ['SA-SAMS export'],
        ['School', BRAND.get('name') or 'United Church School'],
        ['EMIS number', _emis() or '(not set — add SCHOOL_EMIS_NUMBER to the server .env)'],
        ['Province / district', 'Gauteng (GDE)'],
        ['Year', year],
        ['Term', f'Term {term} ({start:%Y-%m-%d} to {end:%Y-%m-%d})'],
        ['Grade(s)', f'Grade {grade}' if grade else 'All grades'],
        ['Marks included', 'Published and draft results' if include_drafts else 'Published results only'],
        ['Generated', timezone.localtime().strftime('%Y-%m-%d %H:%M')],
        [],
        ['Sheets'],
    ]
    descriptions = {
        'Learners': 'Learner register in the SA-SAMS learner-import layout (one row per learner).',
        'Parents': 'Parents / guardians, linked to the learner by admission number and ID number.',
        'Data quality': 'Missing or invalid data to fix before submitting (Errors first).',
    }
    for name, (_headers, data) in (tables or {}).items():
        if name.startswith('Marks Gr'):
            text = 'Mark schedule: learners x subjects, term % and CAPS level.'
        elif name.startswith('Marks T'):
            text = 'All term marks as a list (one row per learner per subject) — for import tools.'
        elif name.startswith('Attendance'):
            text = 'Days present / late / absent per learner for the term, from the daily register.'
        else:
            text = descriptions.get(name, '')
        rows.append([name, f'{text} ({len(data)} rows)'])
    rows += [[], ['Codes']]
    rows.append(['Gender', 'M = Male, F = Female'])
    rows.append(['Population group', ', '.join(f'{code} = {name}' for name, code in
                                               sorted(set(POPULATION_GROUPS.values()), key=lambda x: x[1]))])
    rows.append(['Home language', ', '.join(LANGUAGES) + f', {OTHER_LANGUAGE} (non-SA language)'])
    rows.append(['Dexterity', 'Right, Left, Ambidextrous'])
    rows.append(['Dates', 'YYYY-MM-DD'])
    rows.append(['Achievement level', '; '.join(f'{lvl} = {LEVEL_DESCRIPTORS[lvl]} ({LEVEL_BANDS[lvl]}%)'
                                                for lvl in range(7, 0, -1))])
    rows += [[], ['Assumptions']] + [[f'{i}.', text] for i, text in enumerate(ASSUMPTIONS, 1)]
    rows += [[], ['Sources']] + [[title, url] for title, url in SOURCES]
    return rows


def build_workbook(year, term, grade=None, include_drafts=False, tables=None):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    tables = tables or build_tables(year, term, grade, include_drafts)
    wb = Workbook()
    readme = wb.active
    readme.title = 'Read me'
    bold = Font(bold=True)
    for row in readme_rows(int(year), int(term), grade, include_drafts, tables):
        readme.append(row)
        if len(row) == 1:
            readme.cell(readme.max_row, 1).font = Font(bold=True, size=12)
        elif row:
            readme.cell(readme.max_row, 1).font = bold
    readme.column_dimensions['A'].width = 34
    readme.column_dimensions['B'].width = 120
    for row in readme.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical='top')

    header_fill = PatternFill('solid', fgColor='DDEBF7')
    text_headers = {'Admission Number', 'LURITS Number', 'Learner ID Number', 'Learner Passport Number',
                    'Learner Permit Number', 'Cell Number', 'Home Tel', 'Work Tel',
                    'Parent ID / Passport Number', 'Learner Admission Number', 'EMIS Number'}
    for name, (headers, rows) in tables.items():
        ws = wb.create_sheet(name[:31])
        ws.append(headers)
        for cell in ws[1]:
            cell.font, cell.fill = bold, header_fill
        text_cols = [i for i, h in enumerate(headers, 1) if h in text_headers]
        for row in rows:
            ws.append(row)
            for col in text_cols:                      # keep leading zeros / long numbers
                cell = ws.cell(ws.max_row, col)
                cell.number_format = '@'
                if cell.value not in (None, ''):
                    cell.value = str(cell.value)
        ws.freeze_panes = 'A2'
        for i, header in enumerate(headers, 1):
            width = max([len(str(header))] + [len(str(r[i - 1])) for r in rows[:200] if len(r) >= i])
            ws.column_dimensions[get_column_letter(i)].width = min(max(width + 2, 8), 50)
        if headers:
            ws.auto_filter.ref = f'A1:{get_column_letter(len(headers))}{max(ws.max_row, 1)}'
    return wb


def workbook_bytes(year, term, grade=None, include_drafts=False):
    buffer = io.BytesIO()
    build_workbook(year, term, grade, include_drafts).save(buffer)
    return buffer.getvalue()


def _csv_name(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_').lower() + '.csv'


def csv_zip_bytes(year, term, grade=None, include_drafts=False):
    """A ZIP of one UTF-8 (with BOM, for Excel) CSV per sheet, plus readme.csv."""
    tables = build_tables(year, term, grade, include_drafts)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        sheets = [('Read me', (None, readme_rows(int(year), int(term), grade, include_drafts, tables)))]
        for name, (headers, rows) in sheets + list(tables.items()):
            out = io.StringIO()
            writer = csv.writer(out)
            if headers:
                writer.writerow(headers)
            writer.writerows(rows)
            archive.writestr(_csv_name(name), '﻿' + out.getvalue())
    return buffer.getvalue()


def file_stem(year, term, grade=None):
    return f'sasams_{year}_T{term}' + (f'_gr{int(grade):02d}' if grade else '')
