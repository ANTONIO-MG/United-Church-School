"""
core/school.py  —  United Church School's facts, in one place.

Everything the platform needs to know about the school itself: its grades and
the CAPS phases they fall into, the subjects offered in each grade (and which a
Grade 10 – 12 learner chooses between), the 2026 fee schedule per grade band,
the uniform and additional-fee price list, and the term dates.

Sources
-------
* www.ucs.org.za — the Primary School, High School and Enrolment pages.
* The *UCS Application Form 2026* and *United Church School Fees 2026* PDFs
  published on the Enrolment page (copies in ``static/documents/``). The
  prospectus section of the application form (subjects, term dates, school
  times, fee policy) is the most recent statement and wins where the website's
  older pages differ.
* The national Curriculum and Assessment Policy Statement (CAPS) for the
  subject descriptions and the Grade 10 – 12 subject-choice rules.

``core.academic_spine`` builds the institution → grade → subject structure from
this module; the landing page, the shop seeder and the registration wizard read
the same constants, so a price or subject changes here and nowhere else.
"""
from decimal import Decimal

#: The one institution on the platform.
SCHOOL = {
    'code': 'UCS',
    'name': 'United Church School',
    'accent_name': 'UCS Navy',
    'accent_colour': '#00498B',
    'website': 'https://www.ucs.org.za/',
    'description':
        'An independent, non-denominational, multi-cultural, co-educational school in Yeoville, '
        'Johannesburg, founded in 1990. UCS offers quality education with affordable fees and '
        '"private school" standards from Grade 1 to Grade 12, following the GDE/CAPS curriculum '
        'with English as the medium of instruction. Member of ISASA and registered with the '
        'Gauteng Department of Education.',
}

#: The academic year the fee schedule and calendar below describe.
YEAR = 2026

# --------------------------------------------------------------------------
# Phases (CAPS bands) and the grades in each
# --------------------------------------------------------------------------
PHASE_FOUNDATION = 'foundation'
PHASE_INTERMEDIATE = 'intermediate'
PHASE_SENIOR = 'senior'
PHASE_FET = 'fet'

PHASES = [
    {'code': PHASE_FOUNDATION, 'name': 'Foundation Phase', 'grades': (1, 2, 3),
     'school': 'Primary School', 'campus': '10 Hunters Street, Yeoville'},
    {'code': PHASE_INTERMEDIATE, 'name': 'Intermediate Phase', 'grades': (4, 5, 6),
     'school': 'Primary School', 'campus': '38 Fortesque Road, Yeoville'},
    {'code': PHASE_SENIOR, 'name': 'Senior Phase', 'grades': (7, 8, 9),
     'school': 'High School', 'campus': '44 Frances Street, Yeoville'},
    {'code': PHASE_FET, 'name': 'Further Education and Training (FET) Phase', 'grades': (10, 11, 12),
     'school': 'High School', 'campus': '44 Frances Street, Yeoville'},
]

GRADES = list(range(1, 13))


def phase_for(grade):
    """The PHASES entry a grade belongs to."""
    for phase in PHASES:
        if grade in phase['grades']:
            return phase
    raise ValueError(f'No phase for grade {grade!r}')


def grade_code(grade):
    """``GR01`` … ``GR12`` — the programme code of a grade."""
    return f'GR{int(grade):02d}'


# --------------------------------------------------------------------------
# Subjects — the canonical catalogue (one row per subject however many grades
# teach it; each grade's version is an offering pointing here).
# --------------------------------------------------------------------------
SUBJECTS = [
    {'code': 'ENG-HL', 'name': 'English Home Language', 'order': 1, 'description':
        'Listening and speaking, reading and viewing, writing and presenting, and language '
        'structures and conventions. In the Primary School this covers reading and phonics, '
        'reading and comprehension, spelling and dictation, handwriting, writing and creative '
        'language practice. English is the medium of instruction at UCS.'},
    {'code': 'ZUL-FAL', 'name': 'isiZulu First Additional Language', 'order': 2, 'description':
        'isiZulu as a first additional language: listening and speaking, reading and viewing, '
        'writing and presenting, and language structures and conventions, building toward '
        'confident everyday and academic use.'},
    {'code': 'AFR-FAL', 'name': 'Afrikaans First Additional Language', 'order': 3, 'description':
        'Afrikaans Eerste Addisionele Taal: luister en praat, lees en kyk, skryf en aanbied, en '
        'taalstrukture en -konvensies. Offered in the FET Phase as an alternative to isiZulu FAL.'},
    {'code': 'MATH', 'name': 'Mathematics', 'order': 4, 'description':
        'Numbers, operations and relationships; patterns, functions and algebra; space and shape '
        '(geometry); measurement; and data handling and probability — progressing to functions, '
        'calculus, Euclidean geometry, trigonometry and statistics in the FET Phase.'},
    {'code': 'MLIT', 'name': 'Mathematical Literacy', 'order': 5, 'description':
        'Using mathematics to make sense of real-life situations: finance, measurement, maps and '
        'plans, data handling and probability, applied to personal, workplace and civic contexts. '
        'The FET alternative to Mathematics.'},
    {'code': 'LIFE-SK', 'name': 'Life Skills', 'order': 6, 'description':
        'Personal and social well-being, physical education, creative arts and (in the Foundation '
        'Phase) beginning knowledge — developing healthy, confident, responsible learners. '
        'Supported at UCS by an extra-mural Life Skills development programme and sports.'},
    {'code': 'NST', 'name': 'Natural Sciences and Technology', 'order': 7, 'description':
        'Life and living, matter and materials, energy and change, and planet Earth and beyond, '
        'combined with technology design projects (structures, processing, systems and control).'},
    {'code': 'SOC-SCI', 'name': 'Social Sciences', 'order': 8, 'description':
        'History and Geography: learning about people, places and the past — map skills, '
        'settlement, climate and resources alongside South African and world history.'},
    {'code': 'NAT-SCI', 'name': 'Natural Sciences', 'order': 9, 'description':
        'Life and living, matter and materials, energy and change, and planet Earth and beyond, '
        'laying the foundations for Physical Sciences and Life Sciences.'},
    {'code': 'TECH', 'name': 'Technology', 'order': 10, 'description':
        'The design process applied to structures, processing, mechanical systems and control, '
        'and electrical systems and control — investigating, designing, making and evaluating.'},
    {'code': 'EMS', 'name': 'Economic and Management Sciences', 'order': 11, 'description':
        'The economy, financial literacy and entrepreneurship — needs and wants, the accounting '
        'equation and journals, budgets, and running a small business.'},
    {'code': 'CREATIVE-ARTS', 'name': 'Creative Arts', 'order': 12, 'description':
        'Two art forms (from dance, drama, music and visual arts) — creating, interpreting and '
        'presenting, and appreciating the arts.'},
    {'code': 'LO', 'name': 'Life Orientation', 'order': 13, 'description':
        'Development of the self in society, social and environmental responsibility, democracy '
        'and human rights, careers and career choices, study skills, and physical education.'},
    {'code': 'CODING', 'name': 'Coding and Robotics', 'order': 14, 'description':
        'Computer coding skills, computational thinking, robotics and AI awareness — part of the '
        'UCS curriculum from Grade 1 and resourced through the school levy.'},
    {'code': 'PHYS-SCI', 'name': 'Physical Sciences', 'order': 21, 'description':
        'Mechanics, waves, sound and light, electricity and magnetism, matter and materials, '
        'chemical change and chemical systems, with practical investigations.'},
    {'code': 'LIFE-SCI', 'name': 'Life Sciences', 'order': 22, 'description':
        'Life at the molecular, cellular and tissue level; life processes in plants and animals; '
        'environmental studies; diversity, change and continuity (including evolution and genetics).'},
    {'code': 'HIST', 'name': 'History', 'order': 23, 'description':
        'South African, African and world history from the 1450s to the present — historical '
        'enquiry, source analysis and extended writing.'},
    {'code': 'GEOG', 'name': 'Geography', 'order': 24, 'description':
        'Climate and weather, geomorphology, settlement, economic geography of South Africa, and '
        'mapwork, GIS and fieldwork skills.'},
    {'code': 'ACC', 'name': 'Accounting', 'order': 25, 'description':
        'Financial accounting, managerial accounting and managing resources — the accounting '
        'cycle, financial statements, cost accounting, budgeting, ethics and internal control.'},
    {'code': 'BUS-STUD', 'name': 'Business Studies', 'order': 26, 'description':
        'Business environments, business ventures, business roles and business operations — '
        'from entrepreneurship and legislation to management, leadership and ethics.'},
    {'code': 'ECON', 'name': 'Economics', 'order': 27, 'description':
        'Macroeconomics, microeconomics, economic pursuits and contemporary economic issues — '
        'markets, the circular flow, growth and development, inflation and sustainability.'},
]

# --------------------------------------------------------------------------
# Subject choice in Grade 10 – 12 (CAPS: seven subjects — two official
# languages, Mathematics or Mathematical Literacy, Life Orientation and three
# electives). ``group`` on an offering names the rule it belongs to.
# --------------------------------------------------------------------------
GROUP_FAL = 'fal'
GROUP_MATHS = 'maths'
GROUP_ELECTIVE = 'elective'

#: group → (label shown to the learner, how many to pick)
SUBJECT_GROUPS = {
    GROUP_FAL: ('First Additional Language — choose one', 1),
    GROUP_MATHS: ('Mathematics or Mathematical Literacy — choose one', 1),
    GROUP_ELECTIVE: ('Elective subjects — choose three', 3),
}

# Per-phase offerings: (subject code, group or '' for compulsory, coverage note)
_FOUNDATION = [
    ('ENG-HL', '', ''), ('ZUL-FAL', '', ''), ('MATH', '', ''), ('LIFE-SK', '', ''),
    ('CODING', '', ''),
]
_INTERMEDIATE = [
    ('ENG-HL', '', ''), ('ZUL-FAL', '', ''), ('MATH', '', ''),
    ('NST', '', ''), ('SOC-SCI', '', ''), ('LIFE-SK', '', 'Includes physical education and sport.'),
    ('CODING', '', ''),
]
_SENIOR = [
    ('ENG-HL', '', ''), ('ZUL-FAL', '', ''), ('MATH', '', ''), ('NAT-SCI', '', ''),
    ('SOC-SCI', '', ''), ('TECH', '', ''), ('EMS', '', ''), ('CREATIVE-ARTS', '', ''),
    ('LO', '', ''),
]
_FET = [
    ('ENG-HL', '', ''), ('LO', '', ''),
    ('AFR-FAL', GROUP_FAL, ''), ('ZUL-FAL', GROUP_FAL, ''),
    ('MATH', GROUP_MATHS, ''), ('MLIT', GROUP_MATHS, ''),
    ('PHYS-SCI', GROUP_ELECTIVE, ''), ('LIFE-SCI', GROUP_ELECTIVE, ''),
    ('HIST', GROUP_ELECTIVE, ''), ('GEOG', GROUP_ELECTIVE, ''),
    ('ACC', GROUP_ELECTIVE, ''), ('BUS-STUD', GROUP_ELECTIVE, ''), ('ECON', GROUP_ELECTIVE, ''),
]


def subjects_for(grade):
    """``[(subject code, group, note)]`` offered in ``grade`` (prospectus 2026)."""
    grade = int(grade)
    if grade <= 3:
        return list(_FOUNDATION)
    if grade <= 6:
        return list(_INTERMEDIATE)
    if grade <= 9:
        rows = list(_SENIOR)
        if grade == 7:                       # "Coding (grade 7 only)"
            rows.append(('CODING', '', ''))
        return rows
    return list(_FET)


# --------------------------------------------------------------------------
# Fees 2026 (United Church School Fees 2026). Monthly fees are payable in
# advance on the 1st, January to December. Grade 12 takes no new learners, so
# carries no registration fee.
# --------------------------------------------------------------------------
FEE_BANDS = [
    {'label': 'Grade 1 – 3', 'grades': (1, 2, 3), 'registration': Decimal('550'),
     'levy': Decimal('1900'), 'monthly': Decimal('1200')},
    {'label': 'Grade 4 – 6', 'grades': (4, 5, 6), 'registration': Decimal('550'),
     'levy': Decimal('1900'), 'monthly': Decimal('1250')},
    {'label': 'Grade 7 – 10', 'grades': (7, 8, 9, 10), 'registration': Decimal('550'),
     'levy': Decimal('2200'), 'monthly': Decimal('1800')},
    {'label': 'Grade 11', 'grades': (11,), 'registration': Decimal('550'),
     'levy': Decimal('2200'), 'monthly': Decimal('2200')},
    {'label': 'Grade 12', 'grades': (12,), 'registration': Decimal('0'),
     'levy': Decimal('2200'), 'monthly': Decimal('2750')},
]
for _band in FEE_BANDS:
    _band['annual'] = _band['levy'] + _band['monthly'] * 12
    _band['annual_new'] = _band['annual'] + _band['registration']

#: Discounts from the prospectus (applied to school fees only, never levy or registration).
SIBLING_DISCOUNT_PCT = Decimal('5')      # from the second child onwards
ANNUAL_PREPAY_DISCOUNT_PCT = Decimal('5')  # full year paid by 31 January


def fee_band(grade):
    """The FEE_BANDS entry for a grade."""
    for band in FEE_BANDS:
        if int(grade) in band['grades']:
            return band
    raise ValueError(f'No fee band for grade {grade!r}')


# --------------------------------------------------------------------------
# Uniform and additional fees/expenses (Fees 2026, "Additional Fees/Expenses",
# and the prospectus uniform section). Sold through the school shop.
#   (sku, name, price, category key, fulfilment, sizes, description)
# ``sizes`` is a list of (size label, price adjustment) for ProductVariant rows.
# --------------------------------------------------------------------------
SHIRT_SIZES = [(s, Decimal('0')) for s in
               ('Age 5–6', 'Age 7–8', 'Age 9–10', 'Age 11–12', 'XS', 'S', 'M', 'L', 'XL', 'XXL')]
#: Blazers are priced R700 – R1 100 "depending on sizing". The bands between
#: the published ends are the office's to confirm — edit the variants in the
#: admin (Shop → Products → UCS blazer) once the supplier's list is in.
BLAZER_SIZES = [('Size 26 – 30', Decimal('0')), ('Size 32 – 36', Decimal('150')),
                ('Size 38 – 42', Decimal('300')), ('Size 44 – 48', Decimal('400'))]

SHOP_CATEGORIES = {
    'uniform': ('School Uniform', 'Official UCS uniform items. Blazers and ties are compulsory '
                                  'throughout the year; golf shirts are compulsory.'),
    'fees': ('Additional Fees', 'School services charged to the learner\'s account.'),
}

SHOP_ITEMS = [
    ('UCS-GOLF-PRI', 'UCS golf shirt (Primary School)', Decimal('270'), 'uniform', 'shipped',
     SHIRT_SIZES, 'The official UCS golf shirt for Primary School learners (Grade 1 – 6). Worn for '
                  'Life Skills programmes, sports and special days.'),
    ('UCS-GOLF-HS', 'UCS golf shirt (High School)', Decimal('290'), 'uniform', 'shipped',
     SHIRT_SIZES, 'The official UCS golf shirt for High School learners (Grade 7 – 12). Part of the '
                  'sports and extra-mural uniform.'),
    ('UCS-TIE', 'UCS tie', Decimal('160'), 'uniform', 'shipped', [],
     'The UCS school tie (Primary and High School). Compulsory throughout the year.'),
    ('UCS-CAP', 'UCS cap', Decimal('160'), 'uniform', 'shipped', [],
     'The official UCS cap (Primary and High School).'),
    ('UCS-BADGE', 'UCS badge', Decimal('160'), 'uniform', 'shipped', [],
     'The UCS badge for the blazer and jersey (Primary and High School).'),
    ('UCS-BUTTON', 'UCS blazer button', Decimal('5'), 'uniform', 'shipped', [],
     'Standard UCS blazer buttons, sold individually. No other buttons are permitted.'),
    ('UCS-BLAZER', 'UCS blazer', Decimal('700'), 'uniform', 'shipped', BLAZER_SIZES,
     'The grey UCS blazer with the school badge — compulsory at all times, including when entering '
     'and leaving the premises. Priced R700 – R1 100 depending on size. Blazers are also available '
     'from Gardenia Stores, cnr Joe Slovo & Webb Streets, Yeoville (011 648 6703).'),
    ('UCS-MASK', 'UCS mask', Decimal('60'), 'uniform', 'shipped', [],
     'Reusable UCS-branded face mask.'),
    ('UCS-REPORT-REPRINT', 'Report reprinting', Decimal('90'), 'fees', 'none', [],
     'A reprint of a learner\'s school report.'),
    ('UCS-DRUG-TEST', 'Drug test', Decimal('90'), 'fees', 'none', [],
     'Random drug testing is part of the UCS code of conduct; the testing expense is for the '
     'parent\'s account.'),
    ('UCS-LRC-BADGE', 'LRC badge replacement', Decimal('50'), 'fees', 'none', [],
     'Replacement badge for a member of the Learner Representative Council.'),
]

# --------------------------------------------------------------------------
# The 2026 school year (prospectus, "School terms and times").
#   (term, first day, last day) as (month, day)
# --------------------------------------------------------------------------
TERMS = [
    ('Term 1', (1, 14), (3, 27)),
    ('Term 2', (4, 8), (6, 26)),
    ('Term 3', (7, 21), (9, 23)),
    ('Term 4', (10, 6), (12, 11)),
]

#: Payment deadlines from the fee policy: (title, (month, day), note)
FEE_DATES = [
    ('School fees due — January', (1, 1), 'Registration (where applicable) plus January fees are '
                                          'payable by the 1st of January.'),
    ('Levy due in full', (1, 25), 'The annual levy must be settled in full by 25 January.'),
    ('Annual prepayment discount closes', (1, 31), 'Pay the full annual school fees by 31 January '
                                                   'for a 5% discount.'),
]

#: Banking details for EFT (prospectus, Fees 2026).
BANKING = {
    'bank': 'Standard Bank', 'branch': 'Killarney', 'account_name': 'United Church Schools',
    'account_number': '002181282', 'branch_code': '051001',
    'reference': "the learner's name and grade",
    'proof_to': 'uchs@unitedcs.co.za',
}
