#!/usr/bin/env python
"""
.admin_wipe_and_create.py  —  DESTRUCTIVE database reset utility.

For every database configured in ``config.settings.DATABASES`` this script:

  1. Creates the database if the server does not have it yet, then drops **all**
     tables in it (everything is destroyed — no backup is taken).
  2. Re-runs ``manage.py migrate`` to rebuild the schema from scratch.
  3. Installs **United Church School's academic spine** from
     ``core.academic_spine`` (facts in ``core/school.py``) — the school with its
     crest, Grade 1 to Grade 12 with the 2026 fee schedule, the CAPS subjects
     offered in every grade (with the Grade 10 – 12 subject choices), a class per
     grade for the year, and the school calendar (terms, holidays, fee
     deadlines, public holidays, template exam windows). Then the **school
     shop** (uniform and additional fees, 2026 prices). This is the same data
     ``.demo_seed.py`` enrols its demo learners into: it is defined once, and
     neither script keeps a copy of it.
  4. Creates exactly **four accounts**, one per role — administrator, educator,
     student and parent — each with a verified e-mail, a completed profile and a
     profile picture, so they can sign in immediately with no confirmation step.
     The parent is linked to the student, so the parent-only view has a child to
     look at from the first login. The student is a Grade 10 learner with an
     admitted application and their subjects unlocked, and the educator teaches
     them.
  5. Builds the **General course**: *Getting Started with the UCS Learning
     Platform*, with a generated cover and five areas — Communication · Lessons ·
     Online Classes · Dashboard and Student Matrix · Quizzes and Assessments.
     Each subject carries **one lesson per audience**: one written for learners,
     one for educators and staff, and one for parents. ``Lesson.target_roles``
     keeps them apart, so each role only ever sees its own version.
  6. Creates the chat rooms.
  7. Sends every account a rich **welcome notification** — a long-form
     introduction to the hub, their course, their subjects and what to do first,
     rendered on the notification reading page.

This is the clean base install: the full academic structure, one usable login per
role, and no people in it. It deliberately creates **no sample coursework and no
student body** — run ``.demo_seed.py`` afterwards when you want a populated hub
to demonstrate.

The platform logs in by e-mail, but Django's ``User`` model still keeps an
internal ``username``, so each user's username is the local part of its e-mail.
A ``Person`` profile is created by the ``post_save`` signal in
``apps.accounts.signals``; these accounts are marked onboarded (``registered`` +
``profile_status``) so they skip the onboarding gate.

THE ACCOUNTS (all four share the password ``Password@99``):

    admin@ucs.org.za        superuser — the Django admin at /admin/, full CRUD
    educator@ucs.org.za     teaches Grade 10's subjects
    student@ucs.org.za      a Grade 10 learner, subjects unlocked
    parent@ucs.org.za       linked to the learner, sees their child and nothing else

SETUP ORDER (run from the directory that contains ``manage.py``):

    0) python3.12 -m venv .venv && source .venv/bin/activate
       # the venv MUST be .venv — .env is the settings file this project reads
    1) python .install_requirements.py     # install Python deps first
    2) python .admin_wipe_and_create.py    # THEN reset + seed the database
    3) python .demo_seed.py                # (optional) add the demonstration data

    python .admin_wipe_and_create.py          # asks for confirmation first
    python .admin_wipe_and_create.py --yes     # skip the confirmation prompt

INTENDED FOR LOCAL / DEVELOPMENT USE ONLY.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.db import connections  # noqa: E402

from core import academic_spine, hub_guide, seed_builders, seed_media  # noqa: E402

# The four accounts this script creates — one per role. The administrator is the
# superuser and becomes the author of the guide course; the educator teaches its
# subjects; the student sits them; the parent watches the student.
#   (email, first_name, last_name, user_type, is_superuser)
ACCOUNTS = [
    ("admin@ucs.org.za",    "Gerson",     "Ilha",   "admin",    True),
    ("educator@ucs.org.za", "Tariro",     "Moyo",   "educator", False),
    ("student@ucs.org.za",  "Anesu",      "Sibanda", "student",  False),
    ("parent@ucs.org.za",   "Nomsa",      "Sibanda", "parent",   False),
]
ADMIN_EMAIL = "admin@ucs.org.za"
EDUCATOR_EMAIL = "educator@ucs.org.za"
STUDENT_EMAIL = "student@ucs.org.za"
PARENT_EMAIL = "parent@ucs.org.za"

# Every account signs in with this. Set once, used everywhere below.
PASSWORD = "Password@99"

# Where the seeded learner and educator are placed on the academic spine:
# Grade 10, so the demo shows the FET subject choices.
SPINE_HOME_INSTITUTION = "UCS"
SPINE_HOME_PROGRAMME = "GR10"

# Supplied by the operator; copied into media/ so the pictures are committed.
AVATAR_SOURCE = BASE_DIR.parent / "sample profile pictures"

# Extra profile detail so the seeded accounts do not look half-filled.
#   "person"  → fields on accounts.Person itself
#   "contact" → fields on accounts.PersonContact (the one-to-one detail record)
# These used to be one flat dict written onto Person behind a ``hasattr`` guard,
# which meant every location/phone value was silently dropped: they live on
# PersonContact, not Person. Both records are written now.
#
# Only fields the slimmed registration form still asks for appear here — the
# seeded accounts are meant to look exactly like accounts someone registered
# through the form. ``occupation`` used to sit on the contact records; it was
# dropped from PersonContact in 0022 along with the rest of the removed
# registration questions, so it is gone from here too.
PROFILE_DETAIL = {
    ADMIN_EMAIL: {
        "person": dict(title="mr", gender="male", phone="+27 82 000 0101",
                       primary_device="laptop"),
        "contact": dict(phone_country="ZA", primary_phone="+27 82 000 0101",
                        city="Johannesburg", suburb="Yeoville",
                        province="Gauteng"),
    },
    EDUCATOR_EMAIL: {
        "person": dict(title="ms", gender="female", phone="+27 82 000 0102",
                       primary_device="laptop"),
        "contact": dict(phone_country="ZA", primary_phone="+27 82 000 0102",
                        city="Johannesburg", suburb="Bellevue",
                        province="Gauteng"),
    },
    STUDENT_EMAIL: {
        "person": dict(title="mr", gender="male", phone="+27 82 000 0103",
                       enrolled_class="Grade 10", funding_source="parent",
                       primary_device="phone"),
        "contact": dict(phone_country="ZA", primary_phone="+27 82 000 0103",
                        city="Johannesburg", suburb="Yeoville", province="Gauteng"),
    },
    PARENT_EMAIL: {
        "person": dict(title="mrs", gender="female", phone="+27 82 000 0104",
                       child_name="Anesu Sibanda", funding_source="self",
                       primary_device="phone"),
        "contact": dict(phone_country="ZA", primary_phone="+27 82 000 0104",
                        city="Johannesburg", suburb="Yeoville", province="Gauteng"),
    },
}


def ensure_database(alias):
    """Create the database itself if the server does not have it yet.

    Everything after this point assumes it can connect to ``NAME``; on a fresh
    machine that database has never been created, and Django's own error for
    that ("database ... does not exist") arrives from deep inside a migration
    with no hint about what to do. So connect to the server's maintenance
    database instead and issue a CREATE DATABASE.

    Returns True when the database was created, False when it already existed.
    """
    conn = connections[alias]
    cfg = conn.settings_dict
    name = cfg["NAME"]
    vendor = conn.vendor

    if vendor == "postgresql":
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        # "postgres" is the maintenance database every server has; CREATE
        # DATABASE cannot run inside a transaction, hence autocommit.
        #
        # OPTIONS carries the libpq settings the project's DATABASES entry
        # derived from the environment — sslmode for a managed/remote server,
        # connect_timeout so an unreachable host fails in seconds instead of
        # hanging. Dropping them here would make this admin connection behave
        # differently from every other connection Django opens.
        opts = dict(cfg.get("OPTIONS") or {})
        opts.pop("maintenance_db", None)
        libpq = {k: v for k, v in opts.items() if k in (
            "sslmode", "sslrootcert", "sslcert", "sslkey", "connect_timeout",
            "application_name", "target_session_attrs", "options",
        )}
        host = cfg.get("HOST") or None
        try:
            admin = psycopg2.connect(
                dbname=(cfg.get("OPTIONS", {}).get("maintenance_db", "postgres")),
                user=cfg.get("USER") or None, password=cfg.get("PASSWORD") or None,
                host=host, port=cfg.get("PORT") or None,
                **libpq,
            )
        except psycopg2.OperationalError as exc:
            # The most common failure by far is pointing at Railway's private
            # address from a laptop. psycopg2 reports it as a bare DNS error,
            # which reads like a typo; say what it actually is.
            if host and host.endswith(".railway.internal"):
                raise SystemExit(
                    f"\nCannot reach the database at '{host}'.\n\n"
                    f"That is Railway's *private* hostname: it only resolves "
                    f"from inside Railway's network, never from this machine.\n"
                    f"Fix: open the Railway dashboard → your Postgres service → "
                    f"Variables → copy DATABASE_PUBLIC_URL (its host ends in "
                    f".proxy.rlwy.net and it uses a non-5432 port) into "
                    f"DATABASE_PUBLIC_URL in .env, then re-run.\n"
                    f"If that variable does not exist, enable the TCP proxy "
                    f"under the service's Settings → Networking first.\n\n"
                    f"psycopg2 said: {exc}"
                ) from exc

            # A managed instance (Render, Neon, Supabase, RDS) often hands out a
            # role that can reach only its own database — connecting to
            # "postgres" is refused, and CREATE DATABASE would be refused too.
            # That is not a failure here: the provider already created the
            # database, which is the only thing this function is trying to
            # guarantee. Connecting to it directly both proves that and gets us
            # out of the way of the wipe that follows.
            try:
                probe = psycopg2.connect(
                    dbname=name,
                    user=cfg.get("USER") or None, password=cfg.get("PASSWORD") or None,
                    host=host, port=cfg.get("PORT") or None,
                    **libpq,
                )
            except psycopg2.OperationalError:
                raise exc from None
            probe.close()
            print(f"  → database '{name}' exists on '{alias}' "
                  f"(no access to the 'postgres' maintenance database — "
                  f"normal on a managed instance).")
            return False
        admin.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            with admin.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", [name])
                if cur.fetchone():
                    print(f"  → database '{name}' exists on '{alias}'.")
                    return False
                cur.execute(f'CREATE DATABASE "{name}";')
                owner = cfg.get("USER")
                if owner:
                    cur.execute(f'ALTER DATABASE "{name}" OWNER TO "{owner}";')
                print(f"  → created database '{name}' on '{alias}'.")
                return True
        finally:
            admin.close()

    elif vendor == "mysql":
        import MySQLdb

        admin = MySQLdb.connect(
            user=cfg.get("USER") or "", passwd=cfg.get("PASSWORD") or "",
            host=cfg.get("HOST") or "127.0.0.1", port=int(cfg.get("PORT") or 3306),
        )
        try:
            cur = admin.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{name}` "
                        f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"  → database '{name}' ready on '{alias}'.")
        finally:
            admin.close()
        return True

    # SQLite and anything else: the file/schema is created on first connect.
    print(f"  → '{alias}' ({vendor}) needs no explicit database creation.")
    return False


def drop_all_tables(alias):
    """Remove every table/object owned by the connection ``alias``."""
    conn = connections[alias]
    vendor = conn.vendor
    print(f"  → dropping all tables on '{alias}' ({vendor}) ...")

    with conn.cursor() as cur:
        if vendor == "postgresql":
            # Wiping and recreating the public schema is the cleanest way to
            # drop every table, sequence, view and type in one shot.
            cur.execute("DROP SCHEMA public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            db_user = conn.settings_dict.get("USER")
            if db_user:
                cur.execute(f'GRANT ALL ON SCHEMA public TO "{db_user}";')
            cur.execute("GRANT ALL ON SCHEMA public TO public;")

        elif vendor == "mysql":
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute("SHOW TABLES;")
            tables = [row[0] for row in cur.fetchall()]
            for table in tables:
                cur.execute(f"DROP TABLE IF EXISTS `{table}`;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")

        else:
            # Generic fallback via Django's introspection.
            tables = conn.introspection.table_names(cur)
            sql_list = conn.ops.sql_flush(
                no_style(), tables, reset_sequences=True, allow_cascade=True
            )
            for sql in sql_list:
                cur.execute(sql)

    print(f"    done ({alias}).")


def no_style():
    from django.core.management.color import no_style as _no_style

    return _no_style()


def local_app_labels():
    """App labels for the project's own apps (the ``apps.*`` packages).

    Read from the app registry so customised labels are respected (e.g.
    ``apps.tasks`` registers under the label ``orgtasks``).
    """
    from django.apps import apps as django_apps

    return [
        cfg.label
        for cfg in django_apps.get_app_configs()
        if cfg.name.startswith("apps.")
    ]


def make_migrations():
    """Generate any missing migrations for the project's own apps.

    Several custom apps ship without an ``0001_initial`` migration (and some
    without a ``migrations/`` package at all), so a bare ``migrate`` never
    creates their tables. The app labels are passed explicitly because a
    project-wide ``makemigrations`` silently skips apps with no ``migrations``
    package yet. This is a no-op once the files have been generated.
    """
    labels = local_app_labels()
    print(f"  → generating migrations (makemigrations {' '.join(labels)}) ...")
    call_command("makemigrations", *labels, interactive=False, verbosity=1)
    print("    done.")


def migrate(alias):
    print(f"  → migrating '{alias}' ...")
    call_command("migrate", database=alias, interactive=False, verbosity=1)
    print(f"    done ({alias}).")


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------
def create_accounts(avatars):
    """Create the four accounts, complete their profiles and verify their e-mail.

    Every account ends up immediately usable: the password is set (never left
    unusable), the allauth ``EmailAddress`` is marked verified + primary so the
    login gate passes with no confirmation link, and ``registered`` +
    ``profile_status`` are set so the onboarding middleware lets them straight in.

    Re-running is safe. An account that already exists is *reset* rather than
    skipped — password, role, flags and verification are all re-applied — so a
    half-created or locked-out account is repaired instead of left broken.

    Returns ``{role: Person}``.
    """
    from apps.accounts.models import PersonContact

    User = get_user_model()
    roles = " · ".join(role for _, _, _, role, _ in ACCOUNTS)
    print(f"  → creating the four accounts ({roles}) ...")
    people = {}

    for email, first, last, role, is_super in ACCOUNTS:
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            username = email.split("@", 1)[0]
            maker = User.objects.create_superuser if is_super else User.objects.create_user
            user = maker(username=username, email=email, password=PASSWORD,
                         first_name=first, last_name=last)
            action = "created"
        else:
            # Re-apply everything, so re-running fixes an account rather than
            # leaving it in whatever state it was found in.
            user.first_name, user.last_name = first, last
            user.email = email
            user.is_active = True
            user.set_password(PASSWORD)
            user.save()
            action = "reset   "

        # The admin is the superuser AND reaches the Django admin. Nobody else
        # does — educators teach, students learn, parents watch.
        want_staff, want_super = bool(is_super), bool(is_super)
        if user.is_staff != want_staff or user.is_superuser != want_super:
            user.is_staff, user.is_superuser = want_staff, want_super
            user.save(update_fields=["is_staff", "is_superuser"])

        detail = PROFILE_DETAIL.get(email, {})

        person = getattr(user, "profile", None)   # created by the post_save signal
        if person is None:
            from apps.accounts.models import Person
            person = Person.objects.create(user=user)
        person.first_name = first
        person.last_name = last
        person.user_type = role
        person.registered = True          # skip the registration step
        person.profile_status = True      # skip the profile-completion step
        person.pending_invoice_uid = None  # no enrolment-payment gate
        for field, value in detail.get("person", {}).items():
            setattr(person, field, value)
        person.save()

        contact_fields = detail.get("contact", {})
        if contact_fields:
            PersonContact.objects.update_or_create(person=person, defaults=contact_fields)

        seed_builders.give_face(person, avatars, key=email)
        seed_builders.verify_email(user)   # verified + primary; no confirmation link
        people[role] = person

        flags = " · superuser + Django admin" if is_super else ""
        print(f"    {action} {email:24} ({role}){flags}")

    link_parent_to_student(people)

    print(f"    done — {len(people)} account(s), all verified, "
          f"all on the password '{PASSWORD}'.")
    return people


def link_parent_to_student(people):
    """Point the parent account at the student account.

    One link, not two: ``ParentLink`` is what ``core.scoping`` reads to decide
    which learners a parent may see, and what ParentAccessMiddleware enforces.
    The second link this used to write — ``Person.child_student``, pointing at a
    ``myhub.Student`` row — is gone with the rest of the old MyHub spine; a
    learner *is* a Person on the platform, so there is nothing else to point at.
    """
    from apps.accounts.models import ParentLink

    parent, student = people.get("parent"), people.get("student")
    if parent is None or student is None:
        return

    ParentLink.objects.get_or_create(
        parent=parent.user, student=student.user,
        defaults={"relationship": "Mother"})

    print(f"    linked:  {parent.user.email} → {student.user.email} (parent → student)")


def copy_avatars():
    """Copy the supplied sample profile pictures into ``media/`` (committed)."""
    pool = seed_media.profile_picture_pool(AVATAR_SOURCE)
    if pool:
        print(f"  → {len(pool)} profile picture(s) available in media/profile_pics/seed/")
    else:
        print(f"  → no profile pictures found at {AVATAR_SOURCE} — accounts will use initials.")
    return pool


# ---------------------------------------------------------------------------
# The academic spine — the school, its grades, subjects, fees and calendar
#
# Defined once in ``core.academic_spine`` (facts in ``core/school.py``) and
# installed here. ``.demo_seed.py`` then enrols its demo learners into exactly
# these rows.
# ---------------------------------------------------------------------------
def seed_academic_spine():
    """Install the school, its grades, subjects, fees and calendar, and the shop."""
    print("  → United Church School: grades, subjects, fees and calendar ...")
    result = academic_spine.seed(indent="    ")
    print(f"    {result['events_total']} calendar event(s) for {result['year']} "
          "(term dates published; exam windows unpublished until confirmed)")
    print("  → school shop: uniform and additional fees (2026 prices) ...")
    call_command('seed_shop', '--quiet')
    print("  → demo lessons: Term 1 Week 1, three days per subject in every grade ...")
    try:
        call_command('seed_lessons', verbosity=0)
        from apps.learning.models import Lesson
        print(f"    {Lesson.objects.count()} lesson(s) with quizzes, homework, worksheets and videos")
    except Exception as exc:  # noqa: BLE001 — demo content must never abort a reset
        print(f"    (lessons skipped: {exc})")
    return result


def place_accounts_on_spine(people):
    """Give the seeded learner and educator a real place in the spine.

    The learner is in Grade 10 with an admitted application (filled in the way
    the online application would) and their subjects unlocked; the educator
    teaches the same subjects. Without this the two accounts sign in to an
    empty school.
    """
    from apps.learning.models import Programme

    programme = Programme.objects.filter(institution__code=SPINE_HOME_INSTITUTION,
                                         code=SPINE_HOME_PROGRAMME).first()
    if programme is None:
        print("  → academic spine not present — skipping enrolment.")
        return

    student, educator = people.get("student"), people.get("educator")
    offerings = list(programme.modules.filter(is_active=True))
    if student is not None:
        enrolment, modules = academic_spine.enrol_student(student, programme)
        offerings = [m.programme_module for m in modules]
        cohort = f" · class {enrolment.cohort.code}" if enrolment.cohort else ""
        print(f"  → {student.user.email} registered in {programme.display_name}{cohort} "
              f"— {len(modules)} subject(s) unlocked")
        seed_application(student, programme, people.get("parent"))
    if educator is not None:
        academic_spine.assign_educator(educator, offerings)
        cohort = programme.cohorts.order_by('-code').first()
        if cohort is not None:
            cohort.class_teacher = educator
            cohort.save(update_fields=['class_teacher', 'updated_at'])
        print(f"  → {educator.user.email} teaches {programme.display_name} "
              f"({', '.join(o.code for o in offerings)})")


def seed_application(student, programme, parent):
    """An admitted application for the seeded learner, so the office's
    Admissions pages and the family's My application have a real record."""
    from django.utils import timezone

    from apps.admissions.models import Application, Guardian

    now = timezone.now()
    application, _ = Application.objects.update_or_create(person=student, defaults=dict(
        programme=programme, status=Application.STATUS_ADMITTED, is_new_learner=True,
        highest_grade_passed="Grade 9", year_grade_passed=now.year - 1,
        id_document_type=Application.DOC_SA_ID, id_number="1001015800089",
        is_south_african=True, gender="male", physical_address="12 Raleigh Street, Yeoville, 2198",
        home_language="isiZulu", writing_hand="right", has_father=True, has_mother=True,
        lives_with="Mother", fee_payer="mother", fee_payer_can_afford=True,
        smsweb_number="+27 82 000 0104", previous_school="Yeoville Community School",
        emergency_name="Thandi Dube", emergency_relationship="Aunt",
        emergency_cell_phone="+27 82 000 0199", medical_expenses_name="Nomsa Sibanda",
        medical_expenses_phone="+27 82 000 0104", medical_expenses_relationship="Mother",
        accept_terms=True, accept_indemnity=True, accept_learner_code=True,
        accept_parent_code=True, accept_prospectus=True, accept_fees=True, accept_popia=True,
        acknowledge_documents=True, signed_by="Nomsa Sibanda", signed_relationship="Mother",
        signed_at=now, submitted_at=now, decided_at=now,
        office_pastel_account=True, office_smsweb=True, office_learner_profile=True))
    if parent is not None:
        Guardian.objects.update_or_create(application=application, role=Guardian.ROLE_MOTHER,
                                          defaults=dict(title="Mrs", full_name="Nomsa Sibanda",
                                                        cell_phone="+27 82 000 0104",
                                                        email=parent.user.email,
                                                        invite_sent_at=now))
    print(f"  → admitted application on file for {student.user.email}")


# ---------------------------------------------------------------------------
# The General course
# ---------------------------------------------------------------------------
def seed_onboarding_guide(people):
    """Publish the onboarding guide — one lesson per audience, per area.

    It used to be a Course with five Subjects and everyone enrolled onto it.
    Courses and subjects are gone: what a candidate registers for is a programme
    and its modules, and the guide is neither. It is orientation material that
    belongs to no syllabus, so it is published as role-targeted lessons and every
    account sees its own version without being "enrolled" in anything.
    """
    User = get_user_model()
    admin_user = User.objects.filter(email__iexact=ADMIN_EMAIL).first()

    print("  → publishing the onboarding guide (5 areas × 3 audiences) ...")
    _course, _modules, lessons = hub_guide.build(author=admin_user)
    print(f"    done — {lessons} guide lesson(s), targeted by role.")
    return lessons


def seed_chatrooms():
    """Ensure every course and subject has its own chat room with its members.

    The communication signals create and sync these as enrolment happens; this
    reconciles them explicitly so a freshly-seeded database has them all ready.
    """
    from apps.communication import services
    from apps.learning.models import ProgrammeModule

    print("  → ensuring chat rooms (one per subject in each grade) ...")
    count = 0
    for offering in ProgrammeModule.objects.filter(is_active=True):
        services.sync_module_chat_members(offering)
        count += 1
    print(f"    done — {count} chat room(s) ensured.")


def send_welcomes():
    """Send every account the long-form welcome notification for its role."""
    from apps.accounts.models import Person

    User = get_user_model()
    actor = User.objects.filter(email__iexact=ADMIN_EMAIL).first()

    print("  → sending welcome notifications ...")
    count = 0
    for person in Person.objects.select_related("user").all():
        user = person.user
        if user is None:
            continue
        modules = [m.display_name for m in
                   (person.selected_modules or person.taught_modules.all())]
        sent = seed_builders.send_welcome(
            user,
            title=hub_guide.welcome_title(person),
            summary=hub_guide.welcome_summary(person),
            body_html=hub_guide.welcome_html(person, modules),
            actor=actor if actor and actor.pk != user.pk else None,
            url="/learning/",
        )
        count += 1 if sent else 0
    print(f"    done — {count} welcome notification(s) sent.")


def sync_site():
    """Point django.contrib.sites at SITE_URL.

    The sites framework's initial migration always recreates row 1 as
    "example.com", so a wipe silently reverts whatever the deployment had set.
    Anything that builds an absolute URL from the Site row (allauth's e-mails
    among them) would then send people to example.com. Derive it from SITE_URL,
    which is the one place the public address is configured.
    """
    from django.contrib.sites.models import Site
    from urllib.parse import urlsplit

    domain = urlsplit(getattr(settings, "SITE_URL", "") or "").netloc
    if not domain:
        print("  → SITE_URL is not set — leaving the Site row alone")
        return
    Site.objects.update_or_create(
        pk=getattr(settings, "SITE_ID", 1),
        defaults={"domain": domain, "name": "United Church School"},
    )
    print(f"  → site domain set to {domain} (from SITE_URL)")


def prepare_runtime_dirs():
    """Create the directories the app writes to at run time."""
    dirs = [
        BASE_DIR / "backups" / "archived_accounts",
        BASE_DIR / "media",
        BASE_DIR / "media" / "lessons" / "guide",
        BASE_DIR / "media" / "courses",
        BASE_DIR / "media" / "profile_pics" / "seed",
    ]
    for target in dirs:
        target.mkdir(parents=True, exist_ok=True)
    print("  → runtime dirs ready — backups/, media/ (+ guide, courses, avatars)")


def confirm():
    if "--yes" in sys.argv or "-y" in sys.argv:
        return True
    aliases = ", ".join(settings.DATABASES.keys())
    print("=" * 70)
    print("WARNING — this will PERMANENTLY DROP ALL TABLES on:")
    print(f"  {aliases}")
    print("then re-run migrations and create the four base accounts:")
    for email, _first, _last, role, is_super in ACCOUNTS:
        print(f"    {email:24} ({role}){' · superuser' if is_super else ''}")
    print("=" * 70)
    answer = input("Type 'WIPE' to continue: ").strip()
    return answer == "WIPE"


def main():
    if not confirm():
        print("Aborted. No changes made.")
        sys.exit(1)

    aliases = list(settings.DATABASES.keys())

    print("\n[1/8] Preparing the database (create if missing, then drop everything)")
    for alias in aliases:
        created = ensure_database(alias)
        if not created:
            # A database we just created has nothing in it to drop, and DROP
            # SCHEMA on a brand-new one would only churn.
            drop_all_tables(alias)

    print("\n[2/8] Running migrations")
    make_migrations()
    for alias in aliases:
        migrate(alias)

    print("\n[3/8] Preparing runtime dirs + profile pictures")
    sync_site()
    prepare_runtime_dirs()
    avatars = copy_avatars()

    print("\n[4/8] Building the academic spine "
          "(school · grades · subjects · fees · calendar · shop)")
    spine = seed_academic_spine()

    print("\n[5/8] Creating the four accounts (admin · educator · student · parent)")
    people = create_accounts(avatars)
    place_accounts_on_spine(people)

    print("\n[6/8] Publishing the onboarding guide")
    seed_onboarding_guide(people)

    print("\n[7/8] Ensuring chat rooms")
    seed_chatrooms()

    print("\n[8/8] Sending welcome notifications")
    send_welcomes()

    # Re-lay any bundled content packs (core/seed_packs/) onto the fresh spine so
    # imported lesson material survives a wipe. Best-effort: a pack whose subject
    # isn't on the spine is skipped, and any failure here never aborts the
    # otherwise-complete reset.
    print("\n[+] Importing bundled content packs (core/seed_packs/)")
    try:
        from django.core.management import call_command
        call_command('import_seed_packs')
    except Exception as exc:  # noqa: BLE001
        print(f"    (skipped: {exc})")

    print("\n" + "=" * 70)
    print("All done. The academic spine is installed and four accounts, one per")
    print(f"role, are e-mail-verified and signing in with the password '{PASSWORD}'.")
    print("=" * 70)
    print(f"  School        {spine['institution'].name}")
    print(f"  Grades        {len(spine['programmes'])} · {len(spine['offerings'])} subject offerings "
          f"· {len(spine['modules'])} subjects")
    print(f"  Calendar      {spine['events_total']} dated event(s) for {spine['year']}")
    print()
    for email, first, last, role, is_super in ACCOUNTS:
        tag = " · superuser · /admin/" if is_super else ""
        print(f"  {email:24} {first} {last:9} ({role}){tag}")
    print(f"  {'':24} {PARENT_EMAIL.split('@')[0]} is linked to "
          f"{STUDENT_EMAIL.split('@')[0]}")
    print("\nThe onboarding guide — 'Getting Started with the UCS Learning Platform' —")
    print("has five areas, each with a separate lesson for learners, for")
    print("educators/staff, and for parents. Each role only sees its own.")
    print("\nNext:  python .demo_seed.py     # add people, chat history and financials")
    print("Start: python run_server.py")


if __name__ == "__main__":
    main()
