#!/usr/bin/env python
"""
.04_demo_seed.py  —  STEP 4 of 4 (optional): load the hub with a realistic demo *student body*.

Unlike ``.03_admin.py`` this script is **non-destructive**: it never
drops tables. It only *adds*, and every record it creates is tagged so ``--wipe``
can take it all back out again.

What it seeds — and what it deliberately does not
-------------------------------------------------
This script seeds **people and the records people generate**. It does not invent
any academic structure of its own: institutions, programmes, modules, cohorts and
calendars all come from :mod:`core.academic_spine`, installed by
``.03_admin.py``. There is one definition of the academic world and
this is not it.

It seeds:

* **50 learners** — spread across Grade 1 to Grade 12 (ages matching their
  grade), varied genders, each with a complete profile, a **profile picture**
  and a **verified** e-mail, so they can sign in immediately.
* **4 educators** and **4 parents** (each parent linked to a student, so the
  parent-only view has a real child behind it).
* **Registrations on the real spine** — spread evenly over Grade 1 – 12 per
  ``academic_spine.STUDENT_ALLOCATION``, each with an **application for
  admission** and the grade's subjects.
* **Financial records** — the real enrolment invoice per learner (registration,
  levy and first month's school fees from the grade's fee schedule), with a
  realistic spread of outcomes: most paid (payment, proof and receipt recorded
  through the normal settlement path), some pending payment, and some overdue.
  That is what makes Finance, Admissions, the due-payments list and the subject
  lock/unlock states demonstrable.
* **Conversations** — a class chat group per grade with real traffic, and
  direct messages between random pairs of learners.
* **Personal wall posts** with likes, comments and replies.
* **Personal tasks / reminders** assigned to individual students.
* A **welcome notification** for every account, written for its role.

It does **NOT** seed teaching material. No lessons, no lesson sections, no
topics, no assessments, no attempts. Subject content belongs to the teachers who
author it, not to a demo fixture.

Everything is deterministic (``random.seed``), so re-running gives the same hub.

Usage (from the directory containing ``manage.py``)::

    python .04_demo_seed.py              # seed (safe to re-run — it tops up)
    python .04_demo_seed.py --wipe       # remove every record this script created
    python .04_demo_seed.py --wipe --yes # ... without the confirmation prompt

All demo accounts share the password below and use ``demo.*@ucs.org.za``
e-mails, e.g. ``demo.student01@ucs.org.za`` / ``demo.educator1@ucs.org.za``.

INTENDED FOR LOCAL / DEVELOPMENT USE ONLY.
"""
import os
import random
import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

from core.setup_report import Abort, Report, use_project_venv  # noqa: E402

use_project_venv(__file__)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.db import transaction  # noqa: E402
from django.utils import timezone  # noqa: E402

from apps.accounts.models import ParentLink, Person, PersonContact  # noqa: E402
from apps.communication.models import (  # noqa: E402
    ChatGroup, ChatMembership, Discussion, DiscussionReply, Message, Notification,
)
from apps.finance.models import Invoice, InvoicePayment  # noqa: E402
from apps.learning.models import (  # noqa: E402
    ModuleEnrolment, Programme, ProgrammeEnrolment, ProgrammeModule,
)
from apps.tasks.models import Task  # noqa: E402
from core import academic_spine, hub_guide, seed_builders, seed_media  # noqa: E402

User = get_user_model()

# The same password as the four base accounts in .03_admin.py, so
# there is one password to remember across the whole hub.
PASSWORD = "Password@99"
DEMO_PREFIX = "demo."             # every demo account's e-mail starts with this.
                                  # The base accounts (admin@/educator@/student@/
                                  # parent@ucs.org.za) do NOT carry it, which is
                                  # what keeps --wipe from deleting them.
STUDENT_COUNT = 50
SEED = 20260714                   # deterministic runs

random.seed(SEED)

# --- name pools (Southern-African, matching the base accounts) ---
FIRST_M = ["Anesu", "Farai", "Tendai", "Kudakwashe", "Simba", "Tapiwa", "Blessing",
           "Munashe", "Takudzwa", "Panashe", "Sipho", "Thabo", "Lwazi", "Kagiso",
           "Bongani", "Nkosi", "Themba", "Mpho", "Tinashe", "Rutendo"]
FIRST_F = ["Rudo", "Tariro", "Chipo", "Nyasha", "Ruvarashe", "Vimbai", "Fadzai",
           "Tsitsi", "Nokuthula", "Lerato", "Naledi", "Zanele", "Ayanda", "Thandiwe",
           "Busisiwe", "Refilwe", "Palesa", "Chiedza", "Shamiso", "Danai"]
LAST = ["Moyo", "Ncube", "Dube", "Sithole", "Chirwa", "Banda", "Marimo", "Mutasa",
        "Nyathi", "Mabhena", "Chikafu", "Mhlanga", "Zulu", "Khumalo", "Dlamini",
        "Mokoena", "Sibanda", "Gumbo", "Madziva", "Nkomo", "Chigumba", "Mpofu",
        "Chatambudza", "Rusike", "Mavhunga"]

# South African cities, with the province they sit in — a demo address that does
# not put Sandton in the Western Cape.
PLACES = [
    ("Johannesburg", "Sandton", "Gauteng"), ("Johannesburg", "Rosebank", "Gauteng"),
    ("Pretoria", "Hatfield", "Gauteng"), ("Pretoria", "Menlyn", "Gauteng"),
    ("Cape Town", "Observatory", "Western Cape"), ("Cape Town", "Claremont", "Western Cape"),
    ("Durban", "Umhlanga", "KwaZulu-Natal"), ("Durban", "Berea", "KwaZulu-Natal"),
    ("Gqeberha", "Summerstrand", "Eastern Cape"), ("Bloemfontein", "Westdene", "Free State"),
    ("Polokwane", "Bendor", "Limpopo"), ("Nelspruit", "Sonheuwel", "Mpumalanga"),
]

# Values from the choice lists on accounts.Person, so a demo profile only ever
# holds something the registration form could actually have produced.
TITLES_M = ["mr", "dr"]
TITLES_F = ["ms", "mrs", "miss", "dr"]
FUNDING = ["self", "parent", "employer", "nsfas", "scholarship", "company", "government"]
DEVICES = ["laptop", "laptop", "laptop", "desktop", "tablet", "phone"]

# (email, first, last, gender)
EDUCATORS = [
    ("demo.educator1@ucs.org.za", "Tendai",    "Marimo",  "male"),
    ("demo.educator2@ucs.org.za", "Nyasha",    "Chirwa",  "female"),
    ("demo.educator3@ucs.org.za", "Sipho",     "Khumalo", "male"),
    ("demo.educator4@ucs.org.za", "Ruvarashe", "Mpofu",   "female"),
]

PARENTS = [
    ("demo.parent1@ucs.org.za", "Nomsa",  "Dube",    "female"),
    ("demo.parent2@ucs.org.za", "Joseph", "Sithole", "male"),
    ("demo.parent3@ucs.org.za", "Grace",  "Chirwa",  "female"),
    ("demo.parent4@ucs.org.za", "Peter",  "Banda",   "male"),
]

# --- what people actually talk about here ---------------------------------
# A Grade 1 – 12 school: homework, tests, uniform, sport and the class group.
# Nothing in here implies a subject contains anything the academic spine does
# not say it contains.
CHAT_LINES = [
    "Morning everyone 👋", "Did anyone write down the maths homework?",
    "Page 42, numbers 1 to 10.", "Thank you!",
    "Is the science test on Thursday or Friday?", "Thursday — chapters 3 and 4.",
    "Don't forget blazers tomorrow, there's assembly.",
    "Who's going to the extra lesson after school?", "Count me in.",
    "Reminder: bring your Typek ream for the class.",
    "The English essay is due Monday.", "Can someone explain question 5?",
    "Draw the diagram first — it makes it much easier.",
    "That finally clicked, thank you!", "Good luck for the test tomorrow, everyone.",
    "Extra-murals are on at 13h30 on Thursday.", "Well done on the results 🎉",
    "Is the isiZulu oral next week?", "Yes, Tuesday.",
    "Study group in the library at break?", "See you there.",
]

DM_LINES = [
    "Hey, did you understand today's lesson?",
    "Mostly. The last part about fractions lost me.",
    "Same. Want to go through it together at break?",
    "Yes please. In the library?",
    "Perfect, bring your exercise book.",
    "Will do. Have you started the project?",
    "Barely. Planning to do it this weekend.",
    "Let's compare once we both have something.",
    "Deal. See you tomorrow!",
    "See you 👋",
]

# Posts that land on a learner's OWN wall (their personal feed).
PERSONAL_POSTS = [
    ("Test done ✅", "Not perfect, but I answered everything. Whatever comes back, I studied hard."),
    ("Proud moment", "Got full marks in my spelling test today!"),
    ("My study corner", "Small desk, good light, phone in another room. It really helps."),
    ("Sports day", "Our house won the relay. United we stand! 💙"),
    ("Grateful", "Thank you to whoever explained the science homework in the group last night."),
    ("Note to self", "Read the question twice. It usually tells you exactly what to write."),
    ("Halfway through the term", "Looking back at my first maths test of the year — progress is real."),
    ("Small win", "Finished my reading book this week. On to the next one."),
    ("Extra lessons pay off", "The afternoon extra lessons made the difference this term."),
    ("Back at school", "Holidays were great, but it's good to see everyone again."),
]

REPLIES = [
    "Well done! 🎉", "That helped, thank you!", "I'd like to join the study group.",
    "Same, count me in.", "Great job!", "Keep it up!",
    "Congratulations! Well earned.", "Friday is correct, the calendar is up to date.",
    "Adding mine below.", "Great idea, I might try that.",
    "Practice makes perfect.", "Agreed!",
]

# Personal reminders a teacher sets for a learner. Diary items, not content.
TASK_IDEAS = [
    ("Hand in your project", "Bring your project to class before the deadline.", "high"),
    ("Return the signed letter", "Ask a parent to sign the letter sent home and return it.", "normal"),
    ("Finish your reading log", "Complete this week's reading log.", "normal"),
    ("Catch up on the missed lesson", "You missed a lesson — the notes are on the platform.", "low"),
    ("Study for the test", "Revise the chapters listed for this week's test.", "normal"),
    ("Bring your Typek paper", "Every learner brings one ream of Typek paper this term.", "high"),
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def mark_email_verified(user):
    """Mark ``user``'s e-mail verified + primary so no confirmation link is needed."""
    if not user or not getattr(user, "email", ""):
        return
    try:
        from allauth.account.models import EmailAddress
    except Exception:  # pragma: no cover - allauth optional
        return
    address = EmailAddress.objects.filter(user=user, email__iexact=user.email).first()
    if address is None:
        address = EmailAddress.objects.create(
            user=user, email=user.email, verified=True, primary=True)
    else:
        address.verified = True
        address.primary = True
        address.save(update_fields=["verified", "primary"])
    EmailAddress.objects.filter(user=user).exclude(pk=address.pk).update(primary=False)


def make_user(email, first, last, role, *, contact=None, **person_fields):
    """Create (or top up) a demo user, its Person profile and its contact record.

    ``contact`` is written to :class:`~apps.accounts.models.PersonContact` — the
    same fields the registration form collects, so a demo account looks exactly
    like one somebody registered through the wizard.
    """
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        user = User.objects.create_user(
            username=email.split("@", 1)[0], email=email, password=PASSWORD,
            first_name=first, last_name=last,
        )
    else:
        user.first_name, user.last_name = first, last
        user.save(update_fields=["first_name", "last_name"])

    person = getattr(user, "profile", None)      # created by the post_save signal
    if person is None:
        person = Person.objects.create(user=user)
    person.first_name = first
    person.last_name = last
    person.user_type = role
    person.registered = True
    person.profile_status = True
    for field, value in person_fields.items():
        setattr(person, field, value)
    person.save()

    if contact:
        PersonContact.objects.update_or_create(person=person, defaults=contact)

    mark_email_verified(user)
    return user, person


def backdate(queryset, field, when):
    """Set an ``auto_now_add`` timestamp after the fact (``.update()`` skips auto fields)."""
    queryset.update(**{field: when})


def days_ago(n, hour=9):
    return timezone.now().replace(hour=hour, minute=0, second=0, microsecond=0) - timedelta(days=n)


def _phone():
    return f"+27 8{random.randint(0, 4)} {random.randint(100, 999)} {random.randint(1000, 9999)}"


# ---------------------------------------------------------------------------
# 1. people
# ---------------------------------------------------------------------------
def seed_students():
    """50 students — varied ages and genders, every profile complete."""
    print(f"  → {STUDENT_COUNT} students ...")
    students = []
    today = timezone.now().date()
    for i in range(1, STUDENT_COUNT + 1):
        gender = random.choices(["female", "male", "other"], weights=[47, 47, 6])[0]
        first = random.choice(FIRST_F if gender == "female" else FIRST_M)
        last = random.choice(LAST)
        title = random.choice(TITLES_F if gender == "female" else TITLES_M)
        age = random.randint(7, 18)               # re-set to match the grade once placed
        dob = today - timedelta(days=age * 365 + random.randint(0, 364))
        city, suburb, province = random.choice(PLACES)
        phone = _phone()
        _user, person = make_user(
            f"{DEMO_PREFIX}student{i:02d}@ucs.org.za", first, last, "student",
            title=title, gender=gender, date_of_birth=dob, phone=phone,
            funding_source=random.choice(FUNDING),
            primary_device=random.choice(DEVICES),
            contact={"phone_country": "ZA", "primary_phone": phone,
                     "city": city, "suburb": suburb, "province": province},
        )
        students.append(person)
    print(f"     {len(students)} learners, complete profiles, e-mails verified.")
    return students


def seed_educators():
    print(f"  → {len(EDUCATORS)} educators ...")
    educators = []
    for email, first, last, gender in EDUCATORS:
        city, suburb, province = random.choice(PLACES)
        phone = _phone()
        _user, person = make_user(
            email, first, last, "educator",
            title=random.choice(TITLES_F if gender == "female" else TITLES_M),
            gender=gender, phone=phone,
            date_of_birth=timezone.now().date() - timedelta(days=random.randint(32, 55) * 365),
            primary_device="laptop",
            contact={"phone_country": "ZA", "primary_phone": phone,
                     "city": city, "suburb": suburb, "province": province},
        )
        educators.append(person)
    return educators


def seed_parents(students):
    """Parent accounts, each linked to a student, so the parent-only view works."""
    print(f"  → {len(PARENTS)} parents, linked to students ...")
    parents = []
    for index, (email, first, last, gender) in enumerate(PARENTS):
        child = students[index * 7]               # spread across the grades
        city, suburb, province = random.choice(PLACES)
        phone = _phone()
        _user, person = make_user(
            email, first, last, "parent",
            title=random.choice(TITLES_F if gender == "female" else TITLES_M),
            gender=gender, phone=phone,
            date_of_birth=timezone.now().date() - timedelta(days=random.randint(42, 62) * 365),
            child_name=f"{child.first_name} {child.last_name}",
            funding_source="self", primary_device=random.choice(DEVICES),
            contact={"phone_country": "ZA", "primary_phone": phone,
                     "city": city, "suburb": suburb, "province": province},
        )
        ParentLink.objects.get_or_create(
            parent=person.user, student=child.user,
            defaults={"relationship": "Mother" if gender == "female" else "Father"})
        parents.append(person)
    print(f"     {len(parents)} parents linked.")
    return parents


# ---------------------------------------------------------------------------
# 2. onto the academic spine — the school's grades and subjects
#
# The spine belongs to ``.03_admin.py`` (which installs it from
# ``core.academic_spine``); this only puts people on it. If it is missing —
# someone ran the demo seed against a database that was never built — it is
# installed here rather than leaving the demo learners with no school.
# ---------------------------------------------------------------------------
def seed_spine_enrolments(students, educators):
    """Place the demo learners evenly across Grade 1 – 12.

    Apportioned by ``core.academic_spine.STUDENT_ALLOCATION``. Every learner gets
    a grade enrolment, the grade's subjects (with default Grade 10 – 12
    choices) and an application for admission; their date of birth is set to
    match the grade. The subjects are left LOCKED here — :func:`seed_finances`
    decides who has paid, and unlocking is the payment's job, not a fixture's.

    Teachers are dealt across the offerings that have learners, so every subject
    being studied also has somebody teaching it.
    """
    if not Programme.objects.exists():
        print("  → academic spine missing — installing it first "
              "(normally .03_admin.py does this) ...")
        academic_spine.seed(indent="     ")

    from apps.admissions.models import Application

    pairs = academic_spine.allocate_students(students)
    per_programme = {}
    today = timezone.now().date()
    for person, programme in pairs:
        academic_spine.enrol_student(person, programme, activate=False)
        age = (programme.grade or 6) + 6
        person.date_of_birth = today - timedelta(days=age * 365 + random.randint(0, 300))
        person.enrolled_class = programme.display_name
        person.save(update_fields=['date_of_birth', 'enrolled_class'])
        Application.objects.get_or_create(person=person, defaults=dict(
            programme=programme, gender=person.gender if person.gender in ('male', 'female') else '',
            is_new_learner=random.random() < 0.3, id_document_type=Application.DOC_BIRTH_CERT
            if (programme.grade or 0) < 10 else Application.DOC_SA_ID,
            home_language=random.choice(['isiZulu', 'English', 'Sesotho', 'isiXhosa', 'Shona']),
            lives_with='Parents', fee_payer=random.choice(['mother', 'father', 'both']),
            fee_payer_can_afford=True, smsweb_number=person.phone,
            accept_terms=True, accept_indemnity=True, accept_learner_code=True,
            accept_parent_code=True, accept_prospectus=True, accept_fees=True,
            accept_popia=True, acknowledge_documents=True,
            signed_by=f'Parent of {person.first_name}', signed_relationship='Parent',
            signed_at=timezone.now()))
        per_programme.setdefault(programme, []).append(person)

    print(f"  → {len(pairs)} learner(s) placed across the grades:")
    for programme, people in sorted(per_programme.items(), key=lambda kv: kv[0].grade or 0):
        print(f"     {programme.display_name:9} {len(people):>2} learner(s) "
              f"· R{programme.monthly_fee:,.2f}/month · levy R{programme.annual_levy:,.2f}")

    # Teachers: deal the educators round every offering that has learners on it,
    # rather than round the grades — there are more grades than educators.
    taught = ProgrammeModule.objects.filter(
        enrolments__isnull=False).distinct().order_by('programme_id', 'order', 'id')
    if educators:
        for index, offering in enumerate(taught):
            academic_spine.assign_educator(educators[index % len(educators)], [offering])
    print(f"  → {len(educators)} educator(s) teaching {taught.count()} subject offering(s) "
          f"— every subject with learners has a teacher")
    return per_programme


# ---------------------------------------------------------------------------
# 3. financial records — an invoice per registration, with real outcomes
# ---------------------------------------------------------------------------
#: How the learners divide on money. Roughly two thirds have paid, a small group
#: has just applied (pending payment), and the rest are overdue — which is what
#: makes the due-payments list, Admissions and the locked-subject state all have
#: something to show.
BILLING_SPLIT = [("paid", 0.62), ("pending", 0.14), ("overdue", 0.24)]


def _billing_outcome(index, total):
    """Deterministic outcome for the student at ``index`` of ``total``."""
    cutoff = 0.0
    position = (index + 0.5) / max(total, 1)
    for outcome, share in BILLING_SPLIT:
        cutoff += share
        if position <= cutoff:
            return outcome
    return BILLING_SPLIT[-1][0]


def seed_classes_and_results(per_programme, educators):
    """Give every grade's class a class teacher, and every learner published
    Term 1 and Term 2 results (Term 2 with the mid-year exam from Grade 4), so
    report cards, the parent dashboard and year-end promotion have data."""
    from decimal import Decimal

    from apps.reports.models import TermResult

    teachers = 0
    for index, (programme, people) in enumerate(sorted(per_programme.items(),
                                                       key=lambda kv: kv[0].grade or 0)):
        cohort = programme.cohorts.filter(code=str(timezone.localdate().year)).first() \
            or programme.cohorts.first()
        if cohort is not None and educators and cohort.class_teacher_id is None:
            cohort.class_teacher = educators[index % len(educators)]
            cohort.save(update_fields=['class_teacher', 'updated_at'])
            teachers += 1
    made = 0
    year = timezone.localdate().year
    for programme, people in per_programme.items():
        offerings = list(programme.modules.filter(is_active=True))
        for person in people:
            ability = random.randint(35, 88)
            for offering in offerings:
                if not person.module_enrolments.filter(programme_module=offering).exists():
                    continue
                for term in (1, 2):
                    sba = max(10, min(98, ability + random.randint(-12, 12)))
                    exam = (max(10, min(98, ability + random.randint(-15, 10)))
                            if term == 2 and (programme.grade or 0) >= 4 and offering.code != 'LO' else None)
                    result, created = TermResult.objects.get_or_create(
                        student=person.user, module=offering, year=year, term=term,
                        defaults={'sba_pct': Decimal(sba), 'exam_pct': Decimal(exam) if exam else None,
                                  'status': TermResult.STATUS_PUBLISHED,
                                  'comment': random.choice(['Good effort this term.',
                                                            'Keep practising every day.',
                                                            'Excellent participation in class.',
                                                            'Needs to complete homework regularly.'])})
                    if created:
                        result.recompute()
                        result.published_at = timezone.now()
                        result.save()
                        made += 1
    print(f"  → {teachers} class teacher(s) assigned · {made} published term result(s) (Terms 1 – 2)")


def seed_finances(per_programme):
    """The enrolment invoice per learner, then settle a realistic proportion.

    Payments go through ``apps.finance.services.settle_payment`` rather than
    being written straight to the table, so everything a real payment produces
    comes with them: the payment row, the proof of payment, the receipt e-mail
    hook and — via the ``invoice_paid`` signal — the subject unlock and the
    application moving to review. A fixture
    that inserted rows by hand would look right in the database and wrong
    everywhere else.
    """
    from apps.admissions import services as admissions
    from apps.finance import services as finance_services

    students = [p for people in per_programme.values() for p in people]
    students.sort(key=lambda p: p.user.email)      # stable order → stable outcomes

    made = paid = trialling = overdue = 0
    for index, person in enumerate(students):
        rows = list(ModuleEnrolment.objects.filter(person=person)
                    .select_related('programme_module'))
        if not rows:
            continue
        if Invoice.objects.filter(customer=person.user).exists():
            continue                                # already has money on file

        application = admissions.application_for(person)
        invoice = admissions.raise_enrolment_invoice(person, application, rows)
        admissions.submit(application)
        if invoice is None:                         # a grade with no fees
            for row in rows:
                row.activate(months=6)
            continue
        made += 1

        outcome = _billing_outcome(index, len(students))
        issued = days_ago(random.randint(10, 80))

        if outcome == "paid":
            # Settled through the normal path: this unlocks their subjects too.
            finance_services.settle_payment(
                invoice, invoice.balance,
                gateway=InvoicePayment.GATEWAY_PAYFAST, method='payfast',
                gateway_ref=f'DEMO-{invoice.public_id}',
                reference='demo-seed', raw={'demo': True})
            backdate(InvoicePayment.objects.filter(invoice=invoice), 'created_at', issued)
            # A paid demo learner is an admitted learner (the office would have
            # verified their documents, which the demo does not upload).
            application.status = application.STATUS_ADMITTED
            application.save(update_fields=['status', 'updated_at'])
            paid += 1
        elif outcome == "pending":
            # Just applied: the invoice is out, the subjects wait for payment.
            trialling += 1
        else:
            # Registered, invoiced, never paid — subjects stay locked and the
            # invoice ages into the overdue list.
            overdue += 1

        backdate(Invoice.objects.filter(pk=invoice.pk), 'created_at', issued)

    print(f"  → {made} enrolment invoice(s): {paid} paid (payment + proof recorded), "
          f"{trialling} pending payment, {overdue} outstanding")
    return made


# ---------------------------------------------------------------------------
# 4. conversations
# ---------------------------------------------------------------------------
def _group_chat(group, people, lines, count):
    """Drop ``count`` random messages into ``group``, backdated over ~2 weeks."""
    if group.messages.exists():      # already has traffic — leave it alone
        return 0
    made = 0
    for i in range(count):
        sender = random.choice(people)
        msg = Message.objects.create(group=group, sender=sender.user, body=random.choice(lines))
        backdate(Message.objects.filter(pk=msg.pk), "created_at",
                 days_ago(random.randint(0, 14), hour=random.randint(7, 20)))
        made += 1
    return made


def seed_cohort_chats(per_programme, educators):
    """One chat group per grade — the learners in it, and a teacher.

    A **custom** group: the subject chat groups are built and synced by the
    communication signals off enrolment; a grade's class is a genuine grouping
    of people, which is exactly what a custom group is for.
    """
    made_groups = msgs = 0
    for programme, people in sorted(per_programme.items(), key=lambda kv: kv[0].full_code):
        coach = educators[made_groups % len(educators)] if educators else None
        members = people + ([coach] if coach else [])
        name = f"{programme.display_name} — class cohort chat"

        group = ChatGroup.objects.filter(kind=ChatGroup.KIND_CUSTOM, name=name).first()
        if group is None:
            group = ChatGroup.objects.create(
                kind=ChatGroup.KIND_CUSTOM, name=name,
                created_by=(coach or people[0]).user, is_active=True)
            made_groups += 1
        for person in members:
            ChatMembership.objects.get_or_create(
                group=group, user=person.user,
                defaults={"role": "member", "is_auto": True})
        msgs += _group_chat(group, members, CHAT_LINES, random.randint(12, 22))
    return made_groups, msgs


def seed_direct_messages(students, pairs=30):
    """Random 1-to-1 conversations between students.

    Capped on the total, not just on the pair: the RNG picks different pairs on a
    second run, so a per-pair guard alone would keep adding new conversations.
    """
    existing = (ChatGroup.objects.filter(kind=ChatGroup.KIND_DIRECT,
                                         memberships__user__email__istartswith=DEMO_PREFIX)
                .distinct().count())
    if existing >= pairs:
        return 0, 0

    made_groups = made_msgs = 0
    seen = set()
    for _ in range(pairs - existing):
        a, b = random.sample(students, 2)
        key = tuple(sorted([a.pk, b.pk]))
        if key in seen:
            continue
        seen.add(key)

        if (ChatGroup.objects.filter(kind=ChatGroup.KIND_DIRECT, memberships__user=a.user)
                .filter(memberships__user=b.user).exists()):
            continue

        group = ChatGroup.objects.create(
            kind=ChatGroup.KIND_DIRECT, name="", created_by=a.user, is_active=True)
        ChatMembership.objects.create(group=group, user=a.user, role="owner")
        ChatMembership.objects.create(group=group, user=b.user, role="member")
        made_groups += 1

        start = random.randint(0, 12)
        for i in range(random.randint(4, len(DM_LINES))):
            sender = a if i % 2 == 0 else b
            msg = Message.objects.create(group=group, sender=sender.user, body=DM_LINES[i])
            backdate(Message.objects.filter(pk=msg.pk), "created_at",
                     days_ago(start, hour=random.randint(8, 21)) + timedelta(minutes=i * 7))
            made_msgs += 1
    return made_groups, made_msgs


# ---------------------------------------------------------------------------
# 5. personal walls
# ---------------------------------------------------------------------------
def seed_walls(students):
    """Posts on students' own feeds, with likes, comments and nested replies.

    Personal posts only — a :class:`Discussion` with no course and no subject.
    Class and course walls need one of those to hang off, and there are none.
    """
    if Discussion.objects.filter(author__email__istartswith=DEMO_PREFIX).exists():
        return 0, 0

    posts = replies = 0
    authors = random.sample(students, min(len(PERSONAL_POSTS), len(students)))
    for author, (title, body) in zip(authors, PERSONAL_POSTS):
        post = Discussion.objects.create(author=author.user, title=title, body=body)
        Discussion.objects.filter(pk=post.pk).update(
            created_at=days_ago(random.randint(1, 40), hour=random.randint(8, 21)))
        posts += 1

        for liker in random.sample(students, random.randint(2, 9)):
            post.likes.add(liker.user)

        for _ in range(random.randint(1, 4)):
            commenter = random.choice(students)
            reply = DiscussionReply.objects.create(
                discussion=post, author=commenter.user, body=random.choice(REPLIES))
            DiscussionReply.objects.filter(pk=reply.pk).update(
                created_at=days_ago(random.randint(0, 20), hour=random.randint(8, 21)))
            replies += 1
    return posts, replies


# ---------------------------------------------------------------------------
# 6. personal tasks / reminders
# ---------------------------------------------------------------------------
def seed_tasks(students, educators):
    """A few personal reminders per teacher, assigned to individual learners.

    ``ASSIGN_USER`` only: a task pointed at a subject or a course would need one
    to exist, and diary items are people data — which is what this script seeds.
    """
    if Task.objects.filter(assignee__user__email__istartswith=DEMO_PREFIX).exists():
        return 0
    if not educators:
        return 0

    made = 0
    for person in random.sample(students, min(18, len(students))):
        title, description, priority = random.choice(TASK_IDEAS)
        coach = random.choice(educators)
        Task.objects.create(
            title=title, description=description, priority=priority,
            created_by=coach.user, assign_to=Task.ASSIGN_USER, assignee=person,
            due_date=timezone.now() + timedelta(days=random.randint(-6, 21)),
            status="open",
        )
        made += 1
    return made


# ---------------------------------------------------------------------------
# 7. finishing touches
# ---------------------------------------------------------------------------
def seed_faces(people):
    """Give every demo account a profile picture from the supplied sample set."""
    pool = seed_media.profile_picture_pool(BASE_DIR.parent / "sample profile pictures")
    if not pool:
        print("  → no sample profile pictures found — skipping avatars.")
        return 0
    given = 0
    for person in people:
        if seed_builders.give_face(person, pool, key=person.user.email):
            given += 1
    print(f"  → {given} profile picture(s) assigned from {len(pool)} available.")
    return given


def seed_welcomes(people):
    """The long-form welcome notification for each account, written for its role.

    The "what you're studying" list is the person's registered modules, read off
    the spine — there is nothing else it could be.
    """
    sent = 0
    for person in people:
        # display_name, not module.name — an institution may rename a module on
        # its own programme, and that override is what the student is registered
        # under.
        modules = [
            row.programme_module.display_name
            for row in (ModuleEnrolment.objects.filter(person=person)
                        .select_related('programme_module__module'))]
        if seed_builders.send_welcome(
                person.user,
                title=hub_guide.welcome_title(person),
                summary=hub_guide.welcome_summary(person),
                body_html=hub_guide.welcome_html(person, modules),
                url="/learning/"):
            sent += 1
    return sent


# ---------------------------------------------------------------------------
# wipe
# ---------------------------------------------------------------------------
def wipe():
    """Remove everything this script created (and nothing else)."""
    print("\nRemoving demo data ...")
    demo_users = User.objects.filter(email__istartswith=DEMO_PREFIX)

    # Things that do NOT cascade off the user, or that would outlive them.
    Task.objects.filter(assignee__user__in=demo_users).delete()
    Task.objects.filter(created_by__in=demo_users).delete()
    Discussion.objects.filter(author__in=demo_users).delete()      # cascades replies
    Notification.objects.filter(recipient__in=demo_users).delete()

    n_invoices = Invoice.objects.filter(customer__in=demo_users).count()
    Invoice.objects.filter(customer__in=demo_users).delete()       # cascades items + payments

    # Their chat groups: the cohort groups this script made, and their DMs.
    ChatGroup.objects.filter(kind=ChatGroup.KIND_CUSTOM,
                             name__endswith='cohort chat',
                             memberships__user__in=demo_users).distinct().delete()
    ChatGroup.objects.filter(kind=ChatGroup.KIND_DIRECT,
                             memberships__user__in=demo_users).distinct().delete()

    n_users = demo_users.count()
    n_enrolments = ModuleEnrolment.objects.filter(person__user__in=demo_users).count()
    n_programmes = ProgrammeEnrolment.objects.filter(person__user__in=demo_users).count()
    demo_users.delete()          # cascades Person → its enrolments, messages, links

    print(f"  removed {n_users} demo users, {n_invoices} invoice(s), "
          f"{n_programmes} grade and {n_enrolments} subject enrolment(s), "
          f"and everything hanging off them.")
    print("  the school, grades, subjects and calendar stayed — those are")
    print("  the base install, and the four base accounts were left untouched.")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def confirm(prompt):
    if "--yes" in sys.argv:
        return True
    return input(f"{prompt} [y/N] ").strip().lower() in {"y", "yes"}


def main():
    if "--wipe" in sys.argv:
        if not confirm("Remove ALL demo data (users, registrations, invoices, chat)?"):
            print("Aborted.")
            return
        report = Report("United Church School — Step 4 of 4: remove demo data", "04_demo_seed")
        try:
            with transaction.atomic():
                report.task("remove demo data", wipe,
                            detail="demo users and everything hanging off them; the base install stayed")
        except Abort:
            pass
        sys.exit(report.finish())

    report = Report("United Church School — Step 4 of 4: demo seed", "04_demo_seed")
    print("\nSeeding demo data (safe to re-run — it tops up rather than duplicates)\n")

    per_programme = {}
    try:
        # One transaction: if any step fails, nothing half-seeded is left behind.
        with transaction.atomic():
            students = report.step("demo students", seed_students)
            report.installed("demo students", f"{len(students)} account(s)")
            educators = report.step("demo educators", seed_educators)
            report.installed("demo educators", f"{len(educators)} account(s)")
            per_programme = report.step("grade + subject enrolments", seed_spine_enrolments,
                                        students, educators)
            report.done("grade + subject enrolments", f"{len(per_programme)} grade(s)")
            parents = report.step("demo parents", seed_parents, students)
            report.installed("demo parents", f"{len(parents)} account(s), linked to their children")

            everyone = students + educators + parents
            report.task("profile pictures", seed_faces, everyone)

            print("  → financial records ...")
            report.task("finances", seed_finances, per_programme,
                        detail="invoices: paid, pending and overdue")
            report.task("classes + results", seed_classes_and_results, per_programme, educators)

            print("  → conversations ...")
            groups, group_msgs = report.step("class chats", seed_cohort_chats, per_programme, educators)
            report.done("class chats", f"{groups} group(s), {group_msgs} message(s)")
            dm_groups, dm_msgs = report.step("direct messages", seed_direct_messages, students)
            report.done("direct messages", f"{dm_groups} conversation(s), {dm_msgs} message(s)")

            print("  → walls and reminders ...")
            wall_posts, wall_replies = report.step("wall posts", seed_walls, students)
            report.done("wall posts", f"{wall_posts} post(s), {wall_replies} comment(s) + likes")
            tasks = report.step("reminders", seed_tasks, students, educators)
            report.done("reminders", f"{tasks} assigned")

            print("  → welcome notifications ...")
            sent = report.step("welcome notifications", seed_welcomes, everyone)
            report.done("welcome notifications", f"{sent} sent, each written for the reader's role")
    except Abort:
        report.warn("demo data", "rolled back — nothing from this run was kept")
    except KeyboardInterrupt:
        report.fail("interrupted", "stopped with Ctrl+C — rolled back, nothing was kept")

    if not report.failed:
        grades = sorted(per_programme, key=lambda p: p.grade or 0)
        print(f"\n  Students   demo.student01@ucs.org.za … demo.student{STUDENT_COUNT:02d}@ucs.org.za")
        print(f"  Educators  demo.educator1@ucs.org.za … demo.educator{len(EDUCATORS)}@ucs.org.za")
        print(f"  Parents    demo.parent1@ucs.org.za … demo.parent{len(PARENTS)}@ucs.org.za")
        print(f"  Password   {PASSWORD}   (all e-mails pre-verified)")
        print(f"  Placed     {grades[0].display_name if grades else '—'} to "
              f"{grades[-1].display_name if grades else '—'} — grades and subjects from core/school.py")
        print("  No teaching material is seeded: subject content belongs to whoever authors it.")
    sys.exit(report.finish(
        next_hint="python run.py   (start the platform)  ·  undo with: python3 .04_demo_seed.py --wipe"))


if __name__ == "__main__":
    main()
