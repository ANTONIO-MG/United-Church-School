#!/usr/bin/env python3
"""
.01_install.py  —  STEP 1 of 4: Python, the virtual environment and the packages.

Run the four numbered scripts in order, from the folder that contains manage.py:

    python3 .01_install.py      # 1. Python 3.12–3.14, .environment, requirements.txt
    python3 .02_setup.py        # 2. .env, PostgreSQL, the database, migrations,
                                #    school structure, shop, lessons, verification
    python3 .03_admin.py        # 3. (DESTRUCTIVE) wipe + rebuild the database with
                                #    the five base accounts
    python3 .04_demo_seed.py    # 4. (optional) demo learners, teachers, parents, finances

Then start the platform:  python run.py

Each script prints a report at the end — what was done, what was installed, and
what failed or did not install — and saves it to reports/<script>.txt. At the
end each one offers to run the next.

What this script does:

  1. Checks that the Python running it is one the pinned Django supports
     (Django 6.0 → Python 3.12–3.14). If not, it looks for one on the computer,
     and if there is none it offers to install the newest supported Python
     (Homebrew or pyenv when present; otherwise the official python.org
     installer on macOS, or apt on Debian/Ubuntu). Existing Python installs are
     never modified.
  2. Creates the virtual environment .environment on that Python (rebuilding it
     if it was made with an unsupported one) and re-runs itself inside it — no
     need to activate anything first.
  3. Installs requirements.txt. If the bulk install fails it retries package by
     package so one bad package does not stop the rest, then checks that the
     core packages import, and saves a pip freeze to installed_packages.txt.

Options:

    python3 .01_install.py --yes                 # answer yes to every question
    python3 .01_install.py --python 3.13         # pick the Python version
    python3 .01_install.py --install-python      # allow installing Python without asking
    python3 .01_install.py --no-upgrade-python   # never change the Python, just report
    python3 .01_install.py other-reqs.txt        # a different requirements file

The pinned, known-good snapshot the project runs on is installed_packages.txt;
requirements.txt holds the curated ranges.
"""
import glob
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

from core.setup_report import (  # noqa: E402
    ENV_DIR, Abort, Report, in_project_venv, offer_next,
)

# --------------------------------------------------
# Arguments
# --------------------------------------------------
_argv = sys.argv[1:]
_positional = []
_target_python_arg = None
_i = 0
while _i < len(_argv):
    _a = _argv[_i]
    if _a in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
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
ASSUME_YES = "--yes" in _argv or "-y" in _argv
UPGRADE_PYTHON = not ("--no-upgrade-python" in _argv or "--no-venv-upgrade" in _argv)
ALLOW_INSTALL_PYTHON = "--install-python" in _argv
# Internal sentinel: set on the re-exec so a failed hand-off can't loop forever.
ALREADY_UPGRADED = "--python-upgraded" in _argv

TARGET_PYTHON = None
if _target_python_arg:
    _m = re.match(r"^(\d+)\.(\d+)", _target_python_arg.strip())
    if _m:
        TARGET_PYTHON = (int(_m.group(1)), int(_m.group(2)))
    else:
        print(f"⚠️  Ignoring unparseable --python value: {_target_python_arg!r}\n")

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
    then the *newest* supported minor; ties broken by the highest patch release.
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
    return usable[max(usable)]


PYTHON_ORG_FTP = "https://www.python.org/ftp/python/"


def _latest_python_org_pkg(version):
    """URL of the newest published macOS installer for Python *version* (X.Y).

    python.org creates the X.Y.Z folder before the installer lands in it, so walk
    the patch releases newest-first until one actually has a ``-macos11.pkg``.
    """
    try:
        with urllib.request.urlopen(PYTHON_ORG_FTP, timeout=30) as resp:
            listing = resp.read().decode("utf-8", "replace")
    except OSError as exc:
        print(f"   Could not reach python.org ({exc}).")
        return None
    patches = sorted(
        {int(m) for m in re.findall(rf'href="{re.escape(version)}\.(\d+)/"', listing)},
        reverse=True,
    )
    for patch in patches:
        full = f"{version}.{patch}"
        url = f"{PYTHON_ORG_FTP}{full}/python-{full}-macos11.pkg"
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    return url
        except OSError:
            continue
    return None


def _install_from_python_org(version):
    """Download and run the official python.org installer (macOS). True on success."""
    print(f"   Looking up the latest Python {version} release on python.org…")
    url = _latest_python_org_pkg(version)
    if url is None:
        print(f"   No macOS installer found for Python {version}.")
        return False

    pkg_name = url.rsplit("/", 1)[1]
    print(
        f"   Python {version} can be installed from the official installer:\n"
        f"       {url}\n"
        "   It goes into /Library/Frameworks/Python.framework alongside your "
        "existing Python (which stays untouched). macOS will ask for your password."
    )
    if not (ALLOW_INSTALL_PYTHON or _confirm(f"   Download and install {pkg_name} now?")):
        print("   Skipped — pass --install-python to allow it.\n")
        return False

    tmp_dir = Path(tempfile.mkdtemp(prefix="python-installer-"))
    pkg_path = tmp_dir / pkg_name
    try:
        print(f"   Downloading {pkg_name}…")
        urllib.request.urlretrieve(url, pkg_path)
        print("   Installing (sudo installer)…")
        result = subprocess.run(
            ["sudo", "installer", "-pkg", str(pkg_path), "-target", "/"], check=False
        )
    except OSError as exc:
        print(f"   Download/install failed: {exc}\n")
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    if result.returncode != 0:
        print("   The installer did not finish successfully.\n")
        return False

    # python.org builds ship without a CA bundle; this script links certifi's.
    certs = Path(f"/Applications/Python {version}/Install Certificates.command")
    if certs.exists():
        subprocess.run(["/bin/sh", str(certs)], check=False)
    print(f"   ✅ Python {version} installed.\n")
    return True


def _offer_to_install(min_py, max_py):
    """Fetch a compatible interpreter (pyenv / Homebrew / python.org / apt), with consent."""
    wanted = TARGET_PYTHON if TARGET_PYTHON and min_py <= TARGET_PYTHON <= max_py else max_py
    version = f"{wanted[0]}.{wanted[1]}"

    if shutil.which("pyenv"):
        command = ["pyenv", "install", "-s", version]
    elif shutil.which("brew"):
        command = ["brew", "install", f"python@{version}"]
    elif platform.system() == "Darwin":
        if not _install_from_python_org(version):
            return None
        return _find_interpreter(min_py, max_py)
    elif shutil.which("apt-get"):
        command = [
            "sudo", "apt-get", "install", "-y",
            f"python{version}", f"python{version}-venv", f"python{version}-dev",
        ]
    else:
        print(
            "   No pyenv, Homebrew or apt found — install Python "
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




# --------------------------------------------------
# Step helpers
# --------------------------------------------------
def _venv_python_version(python):
    """(major, minor, micro) of a venv's python, or None if it is missing/broken."""
    if not Path(python).exists():
        return None
    try:
        out = subprocess.run(
            [str(python), "-c", "import sys;print('%d %d %d' % sys.version_info[:3])"],
            capture_output=True, text=True, timeout=30,
        )
        return tuple(int(p) for p in out.stdout.split()) if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _vstr(version):
    return ".".join(str(p) for p in version)


def _reexec(report, python):
    """Continue this run under *python* (inside .environment). Does not return."""
    report.carry()
    argv = [str(python), os.path.abspath(__file__)] + sys.argv[1:]
    if "--python-upgraded" not in argv:
        argv.append("--python-upgraded")
    print(f"\n↪  Continuing inside {ENV_DIR.name} ({python})…\n")
    sys.stdout.flush()
    if os.name == "nt":
        sys.exit(subprocess.run(argv, check=False).returncode)
    os.execv(str(python), argv)


def step_python(report, min_py, max_py, window, django_str):
    """Make sure a supported Python exists. Returns the interpreter to build on."""
    current = sys.version_info[:3]
    if min_py <= current[:2] <= max_py:
        report.done("Python version", f"{_vstr(current)} — Django {django_str} needs {window}")
        return sys.executable

    why = "too old" if current[:2] < min_py else "newer than supported"
    print(f"  Python {_vstr(current)} at {sys.executable} is {why} for Django "
          f"{django_str} (needs {window}).")
    if not UPGRADE_PYTHON:
        report.fail("Python version", f"{_vstr(current)} is {why}; --no-upgrade-python given")
        raise Abort("python")

    print("  🔎 Looking for a supported Python on this computer…")
    match = _find_interpreter(min_py, max_py)
    if match is not None:
        report.done("Python version", f"using installed Python {_vstr(match[0])} at {match[1]} "
                    f"(the default {_vstr(current)} is {why})")
        return match[1]

    print(f"  None of the installed interpreters are in the {window} window.")
    match = _offer_to_install(min_py, max_py)
    if match is None:
        report.fail("Python", f"no Python {window} installed, and it was not installed — "
                    "install it from https://www.python.org/downloads/ and re-run")
        raise Abort("python")
    report.installed(f"Python {_vstr(match[0])}", match[1])
    return match[1]


def step_venv(report, interpreter, min_py, max_py):
    """Create/rebuild .environment on *interpreter*, then re-run inside it."""
    venv_python = ENV_DIR / VENV_BIN / VENV_PY
    if in_project_venv():
        label = f"Virtual environment {ENV_DIR.name}"
        if not any(l == label for _k, l, _d in report.entries):
            report.done(label, f"active (Python {_vstr(sys.version_info[:3])})")
        return

    existing = _venv_python_version(venv_python)
    if existing and min_py <= existing[:2] <= max_py:
        report.done(f"Virtual environment {ENV_DIR.name}", f"exists (Python {_vstr(existing)})")
        _reexec(report, venv_python)

    if ALREADY_UPGRADED:
        report.fail(f"Virtual environment {ENV_DIR.name}",
                    "still not running inside it after re-running — giving up")
        raise Abort("venv")

    if existing:
        print(f"  {ENV_DIR.name} was built on Python {_vstr(existing)}, which Django does "
              "not support — it will be rebuilt (its packages are reinstalled below).")
        if not _confirm(f"  Rebuild {ENV_DIR.name} now?", default=True):
            report.fail(f"Virtual environment {ENV_DIR.name}", "rebuild declined")
            raise Abort("venv")

    new_python = _rebuild_venv(ENV_DIR, interpreter, live=False)
    if new_python is None:
        report.fail(f"Virtual environment {ENV_DIR.name}", f"could not create it with {interpreter}")
        raise Abort("venv")
    version = _venv_python_version(new_python) or ("?",)
    report.installed(f"Virtual environment {ENV_DIR.name}",
                     f"{'rebuilt' if existing else 'created'} on Python {_vstr(version)}")
    _reexec(report, new_python)


def _read_requirements(path):
    packages = []
    skip_prefixes = ("brew ", "export ", "cd ", "python ", "python3 ", "source ",
                     "createdb ", "createuser ", "redis-server", "pip ", "ollama ")
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(skip_prefixes):
                continue
            if "http://" in line or "https://" in line:
                continue
            line = line.split("#", 1)[0].strip()
            if re.match(r"^[A-Za-z0-9_.\-]+", line):
                packages.append(line)
    return packages


def _freeze():
    out = subprocess.run([sys.executable, "-m", "pip", "freeze"],
                         capture_output=True, text=True, check=False)
    versions = {}
    for line in out.stdout.splitlines():
        if "==" in line:
            name, _, version = line.partition("==")
            versions[name.lower()] = (name, version)
    return versions


def _pip(*args, timeout=1800):
    return subprocess.run([sys.executable, "-m", "pip", *args],
                          capture_output=True, text=True, timeout=timeout)


def _last_error_line(result):
    lines = [l for l in (result.stderr or result.stdout or "").splitlines() if l.strip()]
    errors = [l for l in lines if "error" in l.lower()]
    return (errors or lines or ["unknown error"])[-1].strip()[:300]


def step_packages(report):
    if platform.system() == "Linux" and not shutil.which("pg_config") and shutil.which("apt-get"):
        print("  Installing build tools for psycopg2 (build-essential, libpq-dev)…")
        subprocess.run(["sudo", "apt-get", "install", "-y", "build-essential", "libpq-dev"],
                       check=False)

    print("  Upgrading pip, setuptools and wheel…")
    result = _pip("install", "--upgrade", "pip", "setuptools", "wheel")
    if result.returncode == 0:
        report.done("pip, setuptools, wheel", "up to date")
    else:
        report.warn("pip upgrade", _last_error_line(result))

    packages = _read_requirements(REQUIREMENTS_FILE)
    before = _freeze()

    print(f"  Installing {len(packages)} requirement(s) from {REQUIREMENTS_FILE} "
          "(this can take a few minutes)…")
    bulk = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", REQUIREMENTS_FILE],
                          check=False)
    failed = []
    if bulk.returncode != 0:
        report.warn(f"bulk install of {REQUIREMENTS_FILE}",
                    "failed — retrying package by package")
        for index, package in enumerate(packages, 1):
            print(f"  [{index}/{len(packages)}] {package}")
            try:
                result = _pip("install", package, timeout=600)
                ok = result.returncode == 0
                error = "" if ok else _last_error_line(result)
            except subprocess.TimeoutExpired:
                ok, error = False, "timed out after 10 minutes"
            if not ok:
                failed.append(package)
                report.fail(f"package {package}", error)

    after = _freeze()
    new = sorted(after[k][0] + " " + after[k][1] for k in after if k not in before)
    upgraded = sorted(
        f"{after[k][0]} {before[k][1]} → {after[k][1]}"
        for k in after if k in before and before[k][1] != after[k][1]
    )
    for item in new:
        report.installed(item)
    for item in upgraded:
        report.installed(item, "upgraded")
    ok_count = len(packages) - len(failed)
    if not new and not upgraded and not failed:
        report.done(REQUIREMENTS_FILE, f"all {len(packages)} requirement(s) already installed")
    else:
        report.done(REQUIREMENTS_FILE, f"{ok_count}/{len(packages)} requirement(s) satisfied")

    try:
        with open("installed_packages.txt", "w", encoding="utf-8") as fh:
            subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=fh,
                           stderr=subprocess.DEVNULL, check=False)
        report.done("installed_packages.txt", "pip freeze snapshot saved")
    except OSError as exc:
        report.warn("installed_packages.txt", str(exc))

    core = ["django", "psycopg2", "allauth", "rest_framework", "channels", "dotenv"]
    probe = subprocess.run(
        [sys.executable, "-c",
         "import importlib,sys\n"
         "bad=[]\n"
         f"for m in {core!r}:\n"
         "    try: importlib.import_module(m)\n"
         "    except Exception as e: bad.append(m)\n"
         "import django; print(django.get_version()); print(' '.join(bad))"],
        capture_output=True, text=True, check=False,
    )
    lines = probe.stdout.splitlines()
    missing = lines[1].split() if len(lines) > 1 else core
    if probe.returncode == 0 and not missing:
        report.done("core packages import", f"Django {lines[0]}, " + ", ".join(core[1:]))
    else:
        report.fail("core packages import", "missing: " + (", ".join(missing) or "django"))


# --------------------------------------------------
# Main
# --------------------------------------------------
def main():
    report = Report("United Church School — Step 1 of 4: install", "01_install")
    if not Path(REQUIREMENTS_FILE).exists():
        report.fail(REQUIREMENTS_FILE, "not found")
        sys.exit(report.finish())

    floor = _django_floor(REQUIREMENTS_FILE)
    support = _support_window(floor) if floor else None
    if support is None:
        report.fail("Django version", f"could not read the pinned Django from {REQUIREMENTS_FILE}")
        sys.exit(report.finish())
    min_py, max_py = support
    django_str = f"{floor[0]}.{floor[1]}"
    window = f"{min_py[0]}.{min_py[1]}–{max_py[0]}.{max_py[1]}"

    remaining = ["Python version", f"Virtual environment {ENV_DIR.name}", "Python packages"]
    try:
        if not in_project_venv():
            Report.heading(f"1/3  Python (Django {django_str} needs {window})")
            interpreter = report.step("Python", step_python, report, min_py, max_py,
                                      window, django_str)
            remaining.pop(0)
            Report.heading(f"2/3  Virtual environment ({ENV_DIR.name})")
            report.step("Virtual environment", step_venv, report, interpreter, min_py, max_py)
        else:
            # Re-run inside .environment (or started there): the Python is the venv's.
            Report.heading(f"1/3  Python (Django {django_str} needs {window})")
            current = sys.version_info[:3]
            if not (min_py <= current[:2] <= max_py):
                report.fail("Python version", f"{ENV_DIR.name} runs Python {_vstr(current)} — "
                            f"deactivate it and run: python3 {Path(__file__).name}")
                raise Abort("python")
            if not any(label == "Python version" for _k, label, _d in report.entries):
                report.done("Python version", f"{_vstr(current)} — Django {django_str} needs {window}")
            remaining.pop(0)
            Report.heading(f"2/3  Virtual environment ({ENV_DIR.name})")
            step_venv(report, sys.executable, min_py, max_py)
        remaining.pop(0)
        Report.heading("3/3  Python packages")
        report.step("Python packages", step_packages, report)
        remaining.pop(0)
    except Abort:
        report.not_run(remaining[1:])
    except KeyboardInterrupt:
        report.fail("interrupted", "stopped with Ctrl+C")
        report.not_run(remaining[1:])

    code = report.finish(next_hint="python3 .02_setup.py   (database, migrations, school data)")
    if code == 0:
        offer_next(".02_setup.py", "Run step 2 now (.02_setup.py — database, migrations, school data)?")
    sys.exit(code)


if __name__ == "__main__":
    main()
