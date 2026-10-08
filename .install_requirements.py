"""
.install_requirements.py  —  United Church School platform dependency installer.

Installs every package in ``requirements.txt`` one-by-one (so a single failure
doesn't abort the rest) and writes an ``installation_report.txt`` snapshot.
On a new computer run ``bash .setup`` instead — it creates the ``.environment``
virtual environment, installs PostgreSQL and the database from ``.env``, and
calls this script when a bulk ``pip install -r requirements.txt`` fails.

    python .install_requirements.py              # install everything
    python .install_requirements.py --skip-ai    # (kept for compatibility; no-op)
    python .install_requirements.py reqs.txt     # a different requirements file

Before installing anything it checks the running interpreter against the Python
window the pinned Django release supports. If the interpreter is too old (or too
new), it rebuilds **the virtualenv only** on a compatible interpreter already on
the machine and re-runs itself inside it. The system Python is never modified.

    python .install_requirements.py --no-upgrade-python   # just warn, don't rebuild
    python .install_requirements.py --python 3.13         # pick the target version
    python .install_requirements.py --install-python      # allow pyenv/brew to fetch
                                                          #   a missing interpreter

The pinned, known-good version snapshot the project actually runs on lives in
``installed_packages.txt`` (Django 6.0.6 + the stack). ``requirements.txt`` holds
the human-curated ranges; if a fresh install misbehaves, reconcile against
``installed_packages.txt``. Run it inside the project's virtual environment:

    python3.12 -m venv .environment && source .environment/bin/activate

INSTALL ORDER — a new computer, start to finish (macOS or Debian/Ubuntu):

    1) Get the code
         git clone git@github.com:ANTONIO-MG/United-Church-School.git
         cd United-Church-School

    2) Settings — create .env from the example and fill it in
         cp .env.example .env
         # SECRET_KEY, POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD /
         # POSTGRES_HOST / POSTGRES_PORT, SITE_URL, e-mail, USE_REDIS=false,
         # SCHOOL_EMIS_NUMBER (for the SA-SAMS export), PayFast, MS_GRAPH_* …

    3) Everything else in one go
         bash .setup
         # Python 3.12+, the .environment virtual environment, requirements.txt
         # (calls THIS script if a bulk install fails), PostgreSQL, the database
         # and user from .env, migrations, Grade 1 – 12 with CAPS subjects and
         # fees, the 2026 + 2027 GDE calendars, the shop, demo lessons, static
         # files — then it verifies all of it. Safe to run again.

    4) Turn on the environment (every new terminal)
         source .environment/bin/activate

    5) The five base accounts — if .setup did not already create them
         python .admin_wipe_and_create.py    # DESTRUCTIVE: wipes the database first
         # admin@ · staff@ · educator@ · student@ · parent@ucs.org.za
         # all with the password Password@99 — change them before going live

    6) (Optional) demonstration data — learners, teachers, parents, finances
         python .demo_seed.py

    7) Start the platform
         python run.py                       # preflight checks, then http://127.0.0.1:8000
         python run_server.py                # or serve it to the whole network

    8) First things to do in the browser (signed in as admin or staff)
         /staff/class-teachers/   class teacher and subject teachers per grade
         /finance/school-fees/    check the monthly fees per grade
         /sasams/                 enter admission / LURITS numbers, test an export

    Check an existing install at any time:   bash .setup --check
    Packages only (this script):              python .install_requirements.py

Note: the in-browser learning runtimes (SCORM's scorm-again, H5P's h5p-standalone)
are client-side JavaScript loaded from a CDN by default — they add **no** Python
packages here; vendor them into ``static/`` only for an air-gapped/CSP build.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

# --------------------------------------------------
# Requirements file
# --------------------------------------------------

# First non-flag arg is the requirements file; flags control the Python check
# and the local-AI setup.
_argv = sys.argv[1:]
_positional = []
_target_python_arg = None

_i = 0
while _i < len(_argv):
    _a = _argv[_i]
    if _a in ("--python", "--python-version"):
        _target_python_arg = _argv[_i + 1] if _i + 1 < len(_argv) else None
        _i += 2
        continue
    if _a.startswith("--python=") or _a.startswith("--python-version="):
        _target_python_arg = _a.split("=", 1)[1]
    elif not _a.startswith("-"):
        _positional.append(_a)
    _i += 1

REQUIREMENTS_FILE = _positional[0] if _positional else "requirements.txt"
SKIP_AI = "--skip-ai" in _argv or "--no-ai" in _argv
ASSUME_YES = "--yes" in _argv or "-y" in _argv

# Python-version handling
UPGRADE_PYTHON = not ("--no-upgrade-python" in _argv or "--no-venv-upgrade" in _argv)
ALLOW_INSTALL_PYTHON = "--install-python" in _argv
# Internal sentinel: set on the re-exec so a failed upgrade can't loop forever.
ALREADY_UPGRADED = "--python-upgraded" in _argv

TARGET_PYTHON = None
if _target_python_arg:
    _m = re.match(r"^(\d+)\.(\d+)", _target_python_arg.strip())
    if _m:
        TARGET_PYTHON = (int(_m.group(1)), int(_m.group(2)))
    else:
        print(f"⚠️  Ignoring unparseable --python value: {_target_python_arg!r}\n")

installed = []
failed = []
packages = []

# --------------------------------------------------
# Verify file exists
# --------------------------------------------------

if not Path(REQUIREMENTS_FILE).exists():
    print(f"❌ {REQUIREMENTS_FILE} not found.")
    sys.exit(1)

# --------------------------------------------------
# Verify the interpreter satisfies Django's Python requirement
# --------------------------------------------------
# Each Django feature release supports a fixed window of Python versions (see
# https://docs.djangoproject.com/en/stable/faq/install/#what-python-version-can-i-use-with-django).
# We read the pinned Django floor straight from the requirements file and refuse
# to run on an interpreter Django won't support — otherwise pip happily installs
# the whole stack against a Python that can't actually run the project.

# Django X.Y : (min_python, max_python)  inclusive, each as (major, minor)
DJANGO_PYTHON_SUPPORT = {
    (6, 0): ((3, 12), (3, 14)),
    (5, 2): ((3, 10), (3, 13)),
    (5, 1): ((3, 10), (3, 13)),
    (5, 0): ((3, 10), (3, 12)),
    (4, 2): ((3, 8), (3, 12)),
    (4, 1): ((3, 8), (3, 11)),
    (4, 0): ((3, 8), (3, 10)),
    (3, 2): ((3, 6), (3, 10)),
}


def _django_floor(requirements_file):
    """Return the lower-bound Django version (major, minor) pinned in the file."""
    try:
        with open(requirements_file, "r", encoding="utf-8") as fh:
            for raw in fh:
                stripped = raw.split("#", 1)[0].strip()
                # Match the top-level Django requirement, not django-* add-ons.
                if not re.match(r"^[Dd]jango\s*(==|>=|~=|$)", stripped):
                    continue
                m = re.search(r"(?:>=|==|~=)\s*(\d+)\.(\d+)", stripped)
                if m:
                    return (int(m.group(1)), int(m.group(2)))
    except OSError:
        pass
    return None


def _support_window(floor):
    """Return ((min_major, min_minor), (max_major, max_minor)) for a Django floor."""
    support = DJANGO_PYTHON_SUPPORT.get(floor)
    if support is None:
        # Fall back to the closest known Django release at or below the floor.
        candidates = [v for v in DJANGO_PYTHON_SUPPORT if v <= floor]
        if candidates:
            support = DJANGO_PYTHON_SUPPORT[max(candidates)]
    return support


# --------------------------------------------------
# Upgrading the *virtualenv* to a Django-compatible Python
# --------------------------------------------------
# A venv is permanently bound to the interpreter that created it, so "upgrading
# the venv's Python" means rebuilding the venv with a different interpreter.
# Everything below only ever writes inside the venv directory — the system /
# Homebrew / pyenv Python installations are left exactly as they are.

VENV_BIN = "Scripts" if os.name == "nt" else "bin"
VENV_PY = "python.exe" if os.name == "nt" else "python"


def _confirm(question, default=False):
    """Ask a yes/no question. Non-interactive runs fall back to *default*."""
    if ASSUME_YES:
        return True
    if not sys.stdin or not sys.stdin.isatty():
        return default
    try:
        return input(f"{question} [y/N]: ").strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def _interpreter_version(path):
    """Return (major, minor, micro) for *path*, or None if it isn't a usable
    base interpreter (missing, broken, or itself a virtualenv)."""
    try:
        probe = subprocess.run(
            [
                str(path),
                "-c",
                "import sys;print('%d %d %d %d' % (sys.version_info[:3] + "
                "(sys.prefix != sys.base_prefix,)))",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if probe.returncode != 0:
        return None
    parts = probe.stdout.split()
    if len(parts) != 4:
        return None
    try:
        major, minor, micro, is_venv = (int(p) for p in parts)
    except ValueError:
        return None
    # Building a venv from another venv's python works but inherits its quirks;
    # we want a real base installation.
    return None if is_venv else (major, minor, micro)


def _candidate_paths(min_py, max_py):
    """Plausible on-disk locations of pythonX.Y binaries inside the window."""
    names = [
        f"python{min_py[0]}.{minor}"
        for minor in range(min_py[1], max_py[1] + 1)
    ]
    search_dirs = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        "/usr/bin",
        os.path.expanduser("~/.local/bin"),
    ]
    patterns = [
        "/Library/Frameworks/Python.framework/Versions/*/bin/python3.*",
        "/opt/homebrew/opt/python@3.*/bin/python3.*",
        os.path.expanduser("~/.pyenv/versions/*/bin/python3.*"),
    ]

    found = []
    for name in names:
        on_path = shutil.which(name)
        if on_path:
            found.append(on_path)
        found.extend(os.path.join(d, name) for d in search_dirs)
    for pattern in patterns:
        found.extend(glob.glob(pattern))

    # Windows: ask the py launcher what it knows about.
    if os.name == "nt":
        try:
            listing = subprocess.run(
                ["py", "-0p"], capture_output=True, text=True, timeout=30
            )
            for line in listing.stdout.splitlines():
                for token in line.split():
                    if token.lower().endswith("python.exe"):
                        found.append(token)
        except (OSError, subprocess.SubprocessError):
            pass

    # Resolve to the real binary before de-duplicating: a venv's bin/python3.12
    # is a symlink to the base interpreter, and probing the link would wrongly
    # reject that interpreter for living inside a virtualenv.
    seen, unique = set(), []
    for path in found:
        real = os.path.realpath(path)
        if real not in seen and os.path.isfile(real) and os.access(real, os.X_OK):
            seen.add(real)
            unique.append(real)
    return unique


def _find_interpreter(min_py, max_py):
    """Best compatible base interpreter on this machine, or None.

    Preference order: an explicit ``--python X.Y`` if it is inside the window,
    then the *lowest* supported minor (widest wheel coverage for a stack this
    large), then newer ones; ties broken by the highest patch release.
    """
    usable = {}
    for path in _candidate_paths(min_py, max_py):
        version = _interpreter_version(path)
        if version is None:
            continue
        if not (min_py <= version[:2] <= max_py):
            continue
        key = version[:2]
        if key not in usable or version > usable[key][0]:
            usable[key] = (version, path)

    if not usable:
        return None
    if TARGET_PYTHON and TARGET_PYTHON in usable:
        return usable[TARGET_PYTHON]
    if TARGET_PYTHON:
        print(
            f"⚠️  Requested Python {TARGET_PYTHON[0]}.{TARGET_PYTHON[1]} isn't "
            "installed (or is outside Django's window) — picking the best match.\n"
        )
    return usable[min(usable)]


def _offer_to_install(min_py, max_py):
    """Fetch a compatible interpreter via pyenv/Homebrew, with consent."""
    wanted = TARGET_PYTHON if TARGET_PYTHON and min_py <= TARGET_PYTHON <= max_py else min_py
    version = f"{wanted[0]}.{wanted[1]}"

    if shutil.which("pyenv"):
        command = ["pyenv", "install", "-s", version]
    elif shutil.which("brew"):
        command = ["brew", "install", f"python@{version}"]
    else:
        print(
            "   No pyenv or Homebrew found — install Python "
            f"{version} manually (https://www.python.org/downloads/), then re-run.\n"
        )
        return None

    print(
        f"   Python {version} can be installed with:  {' '.join(command)}\n"
        "   This adds a new interpreter system-wide; your existing Python "
        "installs and the system default stay untouched."
    )
    if not (ALLOW_INSTALL_PYTHON or _confirm(f"   Run '{' '.join(command)}' now?")):
        print("   Skipped — pass --install-python to allow it.\n")
        return None

    subprocess.run(command, check=False)
    return _find_interpreter(min_py, max_py)


def _rebuild_venv(venv_dir, interpreter, live):
    """Recreate *venv_dir* using *interpreter*. Returns the new python, or None.

    ``live`` means we are currently running from inside that venv, so the old
    directory is moved aside first (rather than deleted underneath us) and put
    back if creation fails.
    """
    backup = None
    if venv_dir.exists():
        if live and os.name == "nt":
            print(
                "❌ Can't rebuild the running virtualenv on Windows.\n"
                f"   Deactivate it, then run:\n"
                f"       \"{interpreter}\" -m venv --clear \"{venv_dir}\"\n"
                f"       \"{venv_dir}\\{VENV_BIN}\\activate\"\n"
                f"       python {os.path.basename(os.path.abspath(__file__))}\n"
            )
            return None
        backup = venv_dir.with_name(venv_dir.name + ".old")
        shutil.rmtree(backup, ignore_errors=True)
        os.rename(venv_dir, backup)

    result = subprocess.run(
        [str(interpreter), "-m", "venv", str(venv_dir)], check=False
    )
    new_python = venv_dir / VENV_BIN / VENV_PY

    if result.returncode != 0 or not new_python.exists():
        print(f"❌ Failed to create the virtualenv at {venv_dir}.")
        shutil.rmtree(venv_dir, ignore_errors=True)
        if backup is not None:
            os.rename(backup, venv_dir)
            print("   The previous virtualenv has been restored.\n")
        return None

    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)
    return new_python


def _upgrade_virtualenv(min_py, max_py, django_str, window):
    """Move the virtualenv onto a Django-compatible Python and re-exec there.

    On success it replaces this process with the installer running under the new
    interpreter. It only returns when nothing was changed, and the return value
    says whether it already printed usable manual instructions.
    """
    if ALREADY_UPGRADED:
        print("   Already re-ran once after upgrading — not retrying.\n")
        return False
    if not UPGRADE_PYTHON:
        print("   --no-upgrade-python given: leaving the virtualenv alone.\n")
        return False

    print("🔎 Looking for a Python the pinned Django supports…")
    match = _find_interpreter(min_py, max_py)
    if match is None:
        print(f"   None of the installed interpreters are in the {window} window.")
        match = _offer_to_install(min_py, max_py)
    if match is None:
        return False

    version, interpreter = match
    version_str = ".".join(str(p) for p in version)
    print(f"   Found Python {version_str} at {interpreter}\n")

    live = sys.prefix != sys.base_prefix
    if live:
        venv_dir = Path(sys.prefix)
        what = (
            f"♻️  Rebuild the virtualenv {venv_dir} on Python {version_str}?\n"
            f"   Its installed packages are wiped and reinstalled from "
            f"{REQUIREMENTS_FILE} by this run.\n"
            "   Nothing outside the virtualenv is touched."
        )
    else:
        venv_dir = Path(REQUIREMENTS_FILE).resolve().parent / ".environment"
        what = (
            f"ℹ️  Not running inside a virtualenv — the system interpreter will "
            "not be modified.\n"
            f"📦 Create a virtualenv at {venv_dir} on Python {version_str} and "
            "install into it?"
        )

    print(what)
    if not _confirm("   Proceed?", default=False):
        print(
            "   Declined. Do it yourself with:\n"
            f"       \"{interpreter}\" -m venv --clear \"{venv_dir}\"\n"
            f"       source \"{venv_dir}/{VENV_BIN}/activate\"\n"
            f"       python {os.path.basename(os.path.abspath(__file__))}\n"
        )
        return True

    print(f"\n🐍 Building {venv_dir} with Python {version_str}…\n")
    new_python = _rebuild_venv(venv_dir, interpreter, live)
    if new_python is None:
        return False

    print(
        f"✅ Virtualenv now runs Python {version_str} "
        f"(Django {django_str} needs {window}).\n"
        f"   Re-running the installer inside it…\n"
        f"   Remember to re-activate your shell afterwards: "
        f"source {venv_dir}/{VENV_BIN}/activate\n"
    )

    # Hand off to the new interpreter. Nothing below this point runs.
    script = os.path.abspath(__file__)
    argv = [str(new_python), script] + sys.argv[1:] + ["--python-upgraded"]
    sys.stdout.flush()
    if os.name == "nt":
        sys.exit(subprocess.run(argv, check=False).returncode)
    os.execv(str(new_python), argv)


def _check_python_version(requirements_file):
    floor = _django_floor(requirements_file)
    if floor is None:
        print("ℹ️  Could not find a pinned Django version — skipping Python check.\n")
        return

    support = _support_window(floor)
    if support is None:
        print(
            f"ℹ️  No Python compatibility data for Django {floor[0]}.{floor[1]} "
            "— skipping check.\n"
        )
        return

    (min_py, max_py) = support
    current = sys.version_info[:2]
    current_str = ".".join(str(p) for p in sys.version_info[:3])
    django_str = f"{floor[0]}.{floor[1]}"
    window = f"{min_py[0]}.{min_py[1]}–{max_py[0]}.{max_py[1]}"

    if current < min_py:
        print(
            f"❌ Python {current_str} is too old for Django {django_str}+.\n"
            f"   Django {django_str} needs Python {window}.\n"
            f"   Interpreter in use: {sys.executable}\n"
        )
        advised = _upgrade_virtualenv(min_py, max_py, django_str, window)
        # Still here → the venv was not upgraded.
        if not ASSUME_YES:
            if not advised:
                print(
                    "   Fix it manually with:\n"
                    f"       python{min_py[0]}.{min_py[1]} -m venv .environment && "
                    "source .environment/bin/activate\n"
                    "   then re-run this installer with that interpreter."
                )
            sys.exit(1)
        print("⚠️  --yes given: continuing despite the incompatible Python.\n")
        return

    if current > max_py:
        print(
            f"⚠️  Python {current_str} is newer than Django {django_str} officially "
            f"supports ({window}).\n"
        )
        _upgrade_virtualenv(min_py, max_py, django_str, window)
        print("   Continuing, but this combination is untested.\n")
        return

    print(f"✅ Python {current_str} satisfies Django {django_str} (needs {window}).\n")


# Runs before pip touches anything.
_check_python_version(REQUIREMENTS_FILE)

print("🔄 Upgrading pip, setuptools and wheel...\n")

subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
        "setuptools",
        "wheel",
    ],
    check=False,
)

# --------------------------------------------------
# Read and clean requirements file
# --------------------------------------------------

with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        # Skip blank lines
        if not line:
            continue

        # Skip comments
        if line.startswith("#"):
            continue

        # Skip shell commands
        if line.startswith(
            (
                "brew ",
                "export ",
                "cd ",
                "python ",
                "python3 ",
                "source ",
                "createdb ",
                "createuser ",
                "redis-server",
                "pip ",
                "ollama ",
            )
        ):
            continue

        # Skip URLs
        if "http://" in line or "https://" in line:
            continue

        # Remove inline comments
        if "#" in line:
            line = line.split("#", 1)[0].strip()

        # Verify line resembles a package specification
        if not re.match(r"^[A-Za-z0-9_.\-]+", line):
            continue

        packages.append(line)

total = len(packages)

print(f"\n📦 Found {total} package(s) to install\n")

start_time = time.time()

# --------------------------------------------------
# Install packages one by one
# --------------------------------------------------

for index, package in enumerate(packages, start=1):
    print("=" * 80)
    print(f"[{index}/{total}] Installing: {package}")
    print("=" * 80)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package,
            ],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
        )

        if result.returncode == 0:
            print(f"✅ SUCCESS: {package}")
            installed.append(package)

        else:
            print(f"❌ FAILED: {package}")

            failed.append(
                {
                    "package": package,
                    "error": (
                        result.stderr.strip()
                        if result.stderr
                        else "Unknown error"
                    ),
                }
            )

    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {package}")

        failed.append(
            {
                "package": package,
                "error": "Installation timed out after 10 minutes",
            }
        )

    except Exception as e:
        print(f"❌ ERROR: {package}")

        failed.append(
            {
                "package": package,
                "error": str(e),
            }
        )

# --------------------------------------------------
# Summary
# --------------------------------------------------

duration = round(time.time() - start_time, 2)

print("\n")
print("=" * 80)
print("INSTALLATION REPORT")
print("=" * 80)

print(f"\n⏱ Duration: {duration} seconds")
print(f"📦 Total Packages: {total}")
print(f"✅ Installed: {len(installed)}")
print(f"❌ Failed: {len(failed)}")

print("\n" + "=" * 80)
print("SUCCESSFUL INSTALLATIONS")
print("=" * 80)

for pkg in installed:
    print(f"✅ {pkg}")

print("\n" + "=" * 80)
print("FAILED INSTALLATIONS")
print("=" * 80)

for item in failed:
    print(f"\n❌ {item['package']}")
    print(f"   {item['error'][:500]}")

# --------------------------------------------------
# Save report
# --------------------------------------------------

with open("installation_report.txt", "w", encoding="utf-8") as report:
    report.write("INSTALLATION REPORT\n")
    report.write("=" * 80 + "\n\n")

    report.write(f"Requirements File: {REQUIREMENTS_FILE}\n")
    report.write(f"Duration: {duration} seconds\n")
    report.write(f"Total Packages: {total}\n")
    report.write(f"Installed: {len(installed)}\n")
    report.write(f"Failed: {len(failed)}\n\n")

    report.write("=" * 80 + "\n")
    report.write("SUCCESSFUL INSTALLATIONS\n")
    report.write("=" * 80 + "\n\n")

    for pkg in installed:
        report.write(f"{pkg}\n")

    report.write("\n")
    report.write("=" * 80 + "\n")
    report.write("FAILED INSTALLATIONS\n")
    report.write("=" * 80 + "\n\n")

    for item in failed:
        report.write(f"{item['package']}\n")
        report.write(f"{item['error']}\n")
        report.write("-" * 80 + "\n")

print("\n📝 Report saved to installation_report.txt")

# --------------------------------------------------
# Optional: Save installed packages snapshot
# --------------------------------------------------

try:
    with open("installed_packages.txt", "w", encoding="utf-8") as f:
        subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            stdout=f,
            stderr=subprocess.DEVNULL,
            text=True,
        )

    print("📄 Installed package list saved to installed_packages.txt")

except Exception:
    pass

# (The local CrewAI + Ollama AI setup step was retired — live classes are now
#  Microsoft Teams via Microsoft Graph; see docs/TEAMS_INTEGRATION.md.)

# --------------------------------------------------
# Next steps (program initialisation)
# --------------------------------------------------
print("\n" + "=" * 64)
print(" Next steps — the full install order")
print("=" * 64)
_doc = __doc__ or ""
_steps = _doc[_doc.index("INSTALL ORDER"):_doc.index("Note: the in-browser")].rstrip()
print("\n".join("  " + line if line else "" for line in _steps.splitlines()))
print("=" * 64)
