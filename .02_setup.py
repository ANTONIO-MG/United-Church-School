#!/usr/bin/env python3
"""
.02_setup.py  —  STEP 2 of 4: settings, PostgreSQL, the database and the school data.

Run after .01_install.py, from the folder that contains manage.py:

    python3 .02_setup.py            # full setup (asks before installing anything)
    python3 .02_setup.py --check    # only verify an existing setup, change nothing
    python3 .02_setup.py --yes      # answer "yes" to every question

It re-runs itself inside .environment, so there is nothing to activate first.

What it does, in order (safe to run again — every step checks first):

  1. .env — the committed settings file; writes a random SECRET_KEY when it
     is blank. All database settings are read from .env
     (POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST /
     POSTGRES_PORT, or DATABASE_URL).
  2. Environment — the .environment Python and the core packages.
  3. PostgreSQL — finds it (Homebrew, the EDB installer in /Library/PostgreSQL,
     Postgres.app, or the Linux packages), offers to install it when the .env
     database is on this computer and none is installed, and starts it.
  4. The database user and database named in .env, with exactly those
     credentials.
  5. Redis — only when .env turns it on (USE_REDIS=true).
  6. Django — system check, migrations, the school structure (Grade 1 – 12,
     CAPS subjects, fees, a class per grade, the GDE calendars), the school
     shop, bundled content packs, demo lessons, static files, runtime folders.
  7. Verification — database connection, migrations, school data, time zone,
     EMIS number, accounts, and the landing page.

The accounts (admin, staff, educator, student, parent) are step 3:
python3 .03_admin.py
"""
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

from core.setup_report import Abort, Report, ask, offer_next, use_project_venv  # noqa: E402

use_project_venv(__file__)

ASSUME_YES = "--yes" in sys.argv or "-y" in sys.argv
CHECK_ONLY = "--check" in sys.argv
if "-h" in sys.argv or "--help" in sys.argv:
    print(__doc__)
    sys.exit(0)

ENV_FILE = BASE_DIR / ".env"
PG_VERSION = "16"
PLATFORM = {"darwin": "macos", "linux": "linux"}.get(sys.platform, sys.platform)
SUDO = [] if PLATFORM != "linux" or os.geteuid() == 0 else ["sudo"]


def confirm(question):
    return ask(f"  {question}", default=False, assume_yes=ASSUME_YES)


def have(cmd):
    return shutil.which(cmd) is not None


def run(cmd, **kwargs):
    kwargs.setdefault("check", False)
    return subprocess.run(cmd, **kwargs)


def manage(*args, quiet=True):
    """Run a manage.py command; returns the CompletedProcess (output captured if quiet)."""
    cmd = [sys.executable, "manage.py", *args]
    if quiet:
        return run(cmd, capture_output=True, text=True)
    return run(cmd)


def last_error(result):
    text = (getattr(result, "stderr", "") or "") + "\n" + (getattr(result, "stdout", "") or "")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return (lines or ["unknown error"])[-1][:300]


# ---------------------------------------------------------------------------
# 1. .env
# ---------------------------------------------------------------------------
class Config:
    pass


def step_env(report):
    if not ENV_FILE.exists():
        report.fail(".env", "missing — restore it from git:  git checkout -- .env")
        raise Abort(".env")
    report.done(".env", "found")

    from dotenv import dotenv_values
    values = {k: (v or "").strip() for k, v in dotenv_values(ENV_FILE).items()}

    if not values.get("SECRET_KEY"):
        if CHECK_ONLY:
            report.fail("SECRET_KEY", "blank in .env — run without --check to generate one")
        else:
            key = secrets.token_urlsafe(50)
            text = ENV_FILE.read_text(encoding="utf-8")
            pattern = re.compile(r"^[ \t]*SECRET_KEY[ \t]*=.*$", re.M)
            if pattern.search(text):
                text = pattern.sub(lambda _m: f"SECRET_KEY={key}", text, count=1)
            else:
                text = text.rstrip("\n") + f"\nSECRET_KEY={key}\n"
            ENV_FILE.write_text(text, encoding="utf-8")
            values["SECRET_KEY"] = key
            report.installed("SECRET_KEY", "was blank — generated a random one and saved it in .env")
    else:
        report.done("SECRET_KEY", "set")

    cfg = Config()
    url = values.get("DATABASE_URL")
    if url:
        parsed = urlparse(url)
        cfg.name = unquote(parsed.path.lstrip("/"))
        cfg.user = unquote(parsed.username or "")
        cfg.password = unquote(parsed.password or "")
        cfg.host = parsed.hostname or "127.0.0.1"
        cfg.port = str(parsed.port or 5432)
        source = "DATABASE_URL"
    else:
        cfg.name = values.get("POSTGRES_DB") or "united_church_school_db"
        cfg.user = values.get("POSTGRES_USER") or "postgres"
        cfg.password = values.get("POSTGRES_PASSWORD", "")
        cfg.host = values.get("POSTGRES_HOST") or "127.0.0.1"
        cfg.port = values.get("POSTGRES_PORT") or "5432"
        source = "POSTGRES_* settings"
    report.done("database settings", f"from {source}: name={cfg.name} user={cfg.user} "
                f"host={cfg.host}:{cfg.port}")
    if not cfg.password:
        report.fail("POSTGRES_PASSWORD", "empty in .env — the platform refuses a passwordless database")
        raise Abort("password")

    cfg.local = cfg.host in ("", "localhost", "127.0.0.1", "::1") or cfg.host.startswith("/")
    cfg.use_redis = values.get("USE_REDIS", "").lower() in ("true", "1", "yes", "on")
    cfg.redis_url = values.get("REDIS_URL") or "redis://127.0.0.1:6379/1"
    if not values.get("SCHOOL_EMIS_NUMBER"):
        report.warn("SCHOOL_EMIS_NUMBER", "not set in .env — needed before the SA-SAMS export")
    return cfg


# ---------------------------------------------------------------------------
# 2. Environment
# ---------------------------------------------------------------------------
def step_environment(report):
    report.done("Python", f"{sys.version.split()[0]} in .environment")
    missing = []
    for module in ("django", "psycopg2", "allauth", "rest_framework", "dotenv"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        report.fail("core packages", "missing: " + ", ".join(missing)
                    + " — run python3 .01_install.py")
        raise Abort("packages")
    import django
    report.done("core packages", f"Django {django.get_version()}, psycopg2, allauth, DRF")


# ---------------------------------------------------------------------------
# 3. PostgreSQL
# ---------------------------------------------------------------------------
def load_brew():
    if have("brew"):
        return True
    for brew in ("/opt/homebrew/bin/brew", "/usr/local/bin/brew"):
        if os.access(brew, os.X_OK):
            os.environ["PATH"] = f"{Path(brew).parent}:{os.environ['PATH']}"
            return True
    return False


def ensure_brew(report):
    if load_brew():
        return True
    report.warn("Homebrew", "not installed — it is needed to install PostgreSQL / Redis on macOS")
    if not confirm("Install Homebrew now? (it asks for your Mac password)"):
        return False
    result = run(["/bin/bash", "-c",
                  "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
    if result.returncode != 0 or not load_brew():
        report.fail("Homebrew", "the installer failed — see https://brew.sh")
        return False
    report.installed("Homebrew")
    return True


def find_pg_bin():
    """(bin_dir, flavour) of the newest PostgreSQL on this computer, or (None, None)."""
    def newest(pattern, index):
        found = sorted(Path("/").glob(pattern.lstrip("/")),
                       key=lambda p: [int(x) if x.isdigit() else 0
                                      for x in re.split(r"[^\d]+", p.parts[index])],
                       reverse=True)
        return next((p for p in found if (p / "psql").exists()), None)

    edb = newest("/Library/PostgreSQL/*/bin", 3)
    if edb:
        return edb, "edb"
    app = Path("/Applications/Postgres.app/Contents/Versions/latest/bin")
    if (app / "psql").exists():
        return app, "postgresapp"
    if PLATFORM == "macos" and load_brew():
        for formula in (f"postgresql@{PG_VERSION}", "postgresql"):
            out = run(["brew", "--prefix", formula], capture_output=True, text=True)
            prefix = Path(out.stdout.strip() or "/nonexistent") / "bin"
            if out.returncode == 0 and (prefix / "psql").exists():
                return prefix, "homebrew"
    linux = newest("/usr/lib/postgresql/*/bin", 4)
    if linux:
        return linux, "linux"
    if have("psql"):
        return Path(shutil.which("psql")).parent, "path"
    return None, None


def pg_ready(cfg, pg_bin):
    if cfg.host.startswith("/"):
        return Path(cfg.host, f".s.PGSQL.{cfg.port}").exists()
    if pg_bin and (pg_bin / "pg_isready").exists():
        return run([str(pg_bin / "pg_isready"), "-h", cfg.host, "-p", cfg.port],
                   capture_output=True).returncode == 0
    try:
        socket.create_connection((cfg.host, int(cfg.port)), 3).close()
        return True
    except OSError:
        return False


def start_postgres(pg_bin, flavour):
    if flavour == "homebrew" or (PLATFORM == "macos" and flavour == "path" and load_brew()):
        if run(["brew", "services", "start", f"postgresql@{PG_VERSION}"],
               capture_output=True).returncode != 0:
            run(["brew", "services", "start", "postgresql"], capture_output=True)
    elif flavour == "edb":
        edb_dir = pg_bin.parent
        if run(["sudo", "launchctl", "kickstart", "-k",
                f"system/postgresql-{edb_dir.name}"], capture_output=True).returncode != 0:
            run(["sudo", "-u", "postgres", str(pg_bin / "pg_ctl"), "-D",
                 str(edb_dir / "data"), "start"], capture_output=True)
    elif flavour == "postgresapp":
        run(["open", "-a", "Postgres"], capture_output=True)
    else:
        if run(SUDO + ["systemctl", "enable", "--now", "postgresql"],
               capture_output=True).returncode != 0:
            run(SUDO + ["service", "postgresql", "start"], capture_output=True)


def step_postgres(report, cfg):
    if not cfg.local:
        report.done("PostgreSQL", f"database server is remote ({cfg.host}) — nothing to install here")
        return None, None

    pg_bin, flavour = find_pg_bin()
    if pg_bin is None and not CHECK_ONLY:
        report.warn("PostgreSQL", "not installed on this computer")
        if confirm(f"Install PostgreSQL {PG_VERSION} now?"):
            if PLATFORM == "macos":
                if ensure_brew(report):
                    result = run(["brew", "install", f"postgresql@{PG_VERSION}"])
                    if result.returncode == 0:
                        report.installed(f"PostgreSQL {PG_VERSION}", "Homebrew")
            else:
                run(SUDO + ["apt-get", "update", "-y"])
                result = run(SUDO + ["apt-get", "install", "-y", "postgresql", "postgresql-contrib"])
                if result.returncode == 0:
                    report.installed("PostgreSQL", "apt")
            pg_bin, flavour = find_pg_bin()
    if pg_bin is None:
        report.fail("PostgreSQL", "not installed — install it (or answer yes) and re-run")
        raise Abort("postgres")

    version = run([str(pg_bin / "psql"), "--version"], capture_output=True, text=True).stdout.strip()
    report.done("PostgreSQL found", f"{version} ({flavour}) in {pg_bin}")

    if not pg_ready(cfg, pg_bin) and not CHECK_ONLY:
        print("  starting PostgreSQL …")
        start_postgres(pg_bin, flavour)
        for _ in range(20):
            if pg_ready(cfg, pg_bin):
                report.done("PostgreSQL server", "started")
                break
            time.sleep(1)
    if not pg_ready(cfg, pg_bin):
        report.fail("PostgreSQL server", f"not answering on {cfg.host}:{cfg.port}")
        raise Abort("postgres")
    report.done("PostgreSQL server", f"accepting connections on {cfg.host}:{cfg.port}")
    return pg_bin, flavour


# ---------------------------------------------------------------------------
# 4. Database user + database
# ---------------------------------------------------------------------------
ENSURE_SQL = """
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'dbuser', :'dbpass')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'dbuser') \\gexec
SELECT format('ALTER ROLE %I WITH LOGIN PASSWORD %L', :'dbuser', :'dbpass') \\gexec
SELECT format('CREATE DATABASE %I OWNER %I ENCODING ''UTF8'' TEMPLATE template0', :'dbname', :'dbuser')
 WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = :'dbname') \\gexec
SELECT format('GRANT ALL PRIVILEGES ON DATABASE %I TO %I', :'dbname', :'dbuser') \\gexec
"""


def can_connect(cfg, dbname):
    import psycopg2
    try:
        psycopg2.connect(dbname=dbname, user=cfg.user, password=cfg.password,
                         host=cfg.host, port=cfg.port, connect_timeout=5).close()
        return True, ""
    except psycopg2.Error as exc:
        return False, str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__


def create_db_as_user(cfg):
    import psycopg2
    from psycopg2 import sql
    try:
        conn = psycopg2.connect(dbname="postgres", user=cfg.user, password=cfg.password,
                                host=cfg.host, port=cfg.port, connect_timeout=5)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", [cfg.name])
            if not cur.fetchone():
                cur.execute(sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0")
                            .format(sql.Identifier(cfg.name)))
        conn.close()
        return True
    except psycopg2.Error:
        return False


def admin_psql(cfg, pg_bin, flavour, sql_text):
    """Run SQL as the PostgreSQL administrator on this machine."""
    variables = ["-v", "ON_ERROR_STOP=1", "-q", "-v", f"dbuser={cfg.user}",
                 "-v", f"dbpass={cfg.password}", "-v", f"dbname={cfg.name}"]
    env = dict(os.environ)
    psql = str(pg_bin / "psql")
    if flavour == "linux":
        cmd = SUDO + ["-u", "postgres", psql, "-p", cfg.port, "-d", "postgres"] if SUDO \
            else ["su", "postgres", "-c", f"{psql} -p {cfg.port} -d postgres"]
    elif flavour == "edb":
        password = os.environ.get("POSTGRES_ADMIN_PASSWORD")
        if not password:
            import getpass
            password = getpass.getpass("  Password for the PostgreSQL administrator 'postgres' "
                                       "(set when PostgreSQL was installed): ")
        env["PGPASSWORD"] = password
        cmd = [psql, "-h", cfg.host, "-p", cfg.port, "-U", "postgres", "-d", "postgres"]
    else:
        cmd = [psql, "-h", cfg.host, "-p", cfg.port, "-d", "postgres"]
    if cmd[0] == "su":
        return run(cmd, input=sql_text, text=True, env=env).returncode == 0
    return run(cmd + variables, input=sql_text, text=True, env=env).returncode == 0


def step_database(report, cfg, pg_bin, flavour):
    ok, error = can_connect(cfg, cfg.name)
    if ok:
        report.done(f"database '{cfg.name}'", f"exists and '{cfg.user}' can log in with the .env password")
        return
    if CHECK_ONLY or not cfg.local:
        report.fail(f"database '{cfg.name}'", f"cannot log in as '{cfg.user}': {error}")
        raise Abort("database")

    if create_db_as_user(cfg) and can_connect(cfg, cfg.name)[0]:
        report.installed(f"database '{cfg.name}'", f"created as the existing user '{cfg.user}'")
        return

    print("  The .env user cannot create the database on its own — using the PostgreSQL administrator.")
    if admin_psql(cfg, pg_bin, flavour, ENSURE_SQL) and can_connect(cfg, cfg.name)[0]:
        report.installed(f"user '{cfg.user}' + database '{cfg.name}'",
                         "created / password synced from .env")
        return
    ok, error = can_connect(cfg, cfg.name)
    report.fail(f"database '{cfg.name}'", f"could not create it or log in as '{cfg.user}': {error}")
    raise Abort("database")


# ---------------------------------------------------------------------------
# 5. Redis
# ---------------------------------------------------------------------------
def step_redis(report, cfg):
    if not cfg.use_redis:
        report.done("Redis", "USE_REDIS is off — the cache and channels run in memory")
        return
    parsed = urlparse(cfg.redis_url)
    host, port = parsed.hostname or "127.0.0.1", parsed.port or 6379
    if host in ("localhost", "127.0.0.1", "::1") and not have("redis-server") and not CHECK_ONLY \
            and confirm("Redis is not installed. Install Redis now?"):
        if PLATFORM == "macos":
            if ensure_brew(report) and run(["brew", "install", "redis"]).returncode == 0:
                run(["brew", "services", "start", "redis"])
                report.installed("Redis", "Homebrew")
        elif run(SUDO + ["apt-get", "install", "-y", "redis-server"]).returncode == 0:
            run(SUDO + ["systemctl", "enable", "--now", "redis-server"])
            report.installed("Redis", "apt")
    try:
        import redis
        redis.Redis.from_url(cfg.redis_url, socket_connect_timeout=3).ping()
        report.done("Redis", f"answers at {host}:{port}")
    except Exception:  # noqa: BLE001
        report.warn("Redis", f"USE_REDIS=true but {host}:{port} does not answer — start Redis, "
                    "or set USE_REDIS=false in .env for a single-computer setup")


# ---------------------------------------------------------------------------
# 6. Django
# ---------------------------------------------------------------------------
def step_django(report):
    result = manage("check")
    if result.returncode == 0:
        report.done("Django system check", "passed")
    else:
        print(result.stdout[-3000:], result.stderr[-3000:], sep="\n")
        report.fail("Django system check", last_error(result))
        raise Abort("check")
    if CHECK_ONLY:
        return

    print("  applying migrations …")
    result = manage("migrate", "--noinput")
    if result.returncode != 0:
        print(result.stdout[-3000:], result.stderr[-3000:], sep="\n")
        report.fail("migrations", last_error(result))
        raise Abort("migrate")
    applied = len(re.findall(r"^\s+Applying ", result.stdout, re.M))
    report.done("migrations", f"{applied} applied" if applied else "already up to date")
    manage("migrate", "captcha", "--noinput")

    tasks = [
        (("seed_school_structure",), "school structure",
         "Grade 1 – 12, CAPS subjects, fees, a class per grade, calendars", True),
        (("seed_shop", "--quiet"), "school shop", "uniform and additional fees", True),
        (("import_seed_packs",), "content packs", "bundled packs imported", False),
        (("seed_lessons",), "demo lessons", "3 days per subject in every grade (Term 1 Week 1)", False),
        (("collectstatic", "--noinput"), "static files", "collected", False),
    ]
    for args, label, detail, important in tasks:
        print(f"  {label} …")
        result = manage(*args)
        if result.returncode == 0:
            report.done(label, detail)
        elif important:
            report.fail(label, f"python manage.py {' '.join(args)}: {last_error(result)}")
        else:
            report.warn(label, f"not done — python manage.py {' '.join(args)}: {last_error(result)}")

    for folder in ("media/scorm", "media/h5p", "backups/archived_accounts"):
        (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)
    report.done("runtime folders", "media/scorm, media/h5p, backups/archived_accounts")


# ---------------------------------------------------------------------------
# 7. Verification
# ---------------------------------------------------------------------------
def step_verify(report):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from io import StringIO

    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.core.management import call_command
    from django.db import connection
    from django.test import Client
    from django.test.utils import setup_test_environment

    def check(label, good, detail=""):
        (report.done if good else report.fail)(f"verify: {label}", detail)

    with connection.cursor() as cur:
        cur.execute("select current_database(), current_user, version()")
        db, user, version = cur.fetchone()
    check("database connection", True, f"{db} as {user} ({version.split(',')[0]})")

    out = StringIO()
    call_command("showmigrations", "--plan", stdout=out)
    pending = sum(1 for line in out.getvalue().splitlines() if line.startswith("[ ]"))
    check("migrations", pending == 0, "all applied" if not pending else f"{pending} not applied")
    if pending:
        report.not_run(["verify: school data, accounts, landing page"],
                       "the database is not migrated — run python3 .02_setup.py")
        return

    from apps.learning.models import AcademicCalendar, Cohort, Institution, Lesson, Programme, ProgrammeModule
    from apps.shop.models import Product
    school = Institution.objects.filter(code="UCS").first()
    check("school", school is not None, school.name if school else "missing — python manage.py seed_school_structure")
    grades = Programme.objects.filter(institution=school).count() if school else 0
    check("grades", grades == 12, f"{grades} grade(s), {ProgrammeModule.objects.count()} subject offerings")
    check("school shop", Product.objects.filter(sku__startswith="UCS-").exists(),
          f"{Product.objects.filter(status='active').count()} active product(s)")
    years = sorted(AcademicCalendar.objects.values_list("year", flat=True).distinct())
    check("school calendars", bool(years), ", ".join(map(str, years)) or "missing")
    lessons = Lesson.objects.count()
    if lessons:
        check("demo lessons", True, f"{lessons} lesson(s)")
    else:
        report.warn("verify: demo lessons", "none — optional: python manage.py seed_lessons")
    classes = Cohort.objects.filter(programme__institution=school).count() if school else 0
    with_teacher = Cohort.objects.filter(programme__institution=school,
                                         class_teacher__isnull=False).count() if school else 0
    check("classes", classes > 0, f"{classes} class(es), {with_teacher} with a class teacher")
    check("time zone", settings.TIME_ZONE == "Africa/Johannesburg", settings.TIME_ZONE)

    users = get_user_model().objects.count()
    if users:
        check("accounts", True, f"{users} account(s)")
    else:
        report.warn("verify: accounts", "none yet — step 3 creates them: python3 .03_admin.py")

    setup_test_environment()
    host = settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS and settings.ALLOWED_HOSTS[0] != "*" else "localhost"
    response = Client(SERVER_NAME=host).get("/social/landing/")
    check("landing page", response.status_code < 400, f"HTTP {response.status_code}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    mode = " (check only)" if CHECK_ONLY else ""
    report = Report(f"United Church School — Step 2 of 4: setup{mode}", "02_setup")
    steps = ["1/7  Configuration (.env)", "2/7  Environment", "3/7  PostgreSQL",
             "4/7  Database and user", "5/7  Redis", "6/7  Django application", "7/7  Verification"]
    remaining = list(steps)

    def heading():
        Report.heading(remaining[0])

    try:
        heading(); cfg = report.step(".env", step_env, report); remaining.pop(0)
        heading(); report.step("environment", step_environment, report); remaining.pop(0)
        heading(); pg_bin, flavour = report.step("PostgreSQL", step_postgres, report, cfg); remaining.pop(0)
        heading(); report.step("database", step_database, report, cfg, pg_bin, flavour); remaining.pop(0)
        heading(); report.step("Redis", step_redis, report, cfg, critical=False); remaining.pop(0)
        heading(); report.step("Django application", step_django, report); remaining.pop(0)
        heading(); report.step("verification", step_verify, report); remaining.pop(0)
    except Abort:
        report.not_run(remaining[1:])
    except KeyboardInterrupt:
        report.fail("interrupted", "stopped with Ctrl+C")
        report.not_run(remaining[1:])

    code = report.finish(next_hint="python3 .03_admin.py   (DESTRUCTIVE: wipe + the five base accounts)")
    if code == 0 and not CHECK_ONLY:
        offer_next(".03_admin.py", "Run step 3 now (.03_admin.py — wipes the database and creates "
                   "the five base accounts)?")
    sys.exit(code)


if __name__ == "__main__":
    main()
