"""Shared plumbing for the numbered setup scripts (.01_install.py … .04_demo_seed.py).

Pure standard library and Python 3.9-compatible: ``.01_install.py`` imports it
while it may still be running on an old system Python, before Django or any
other package is installed.

* ``Report`` collects what each step did and prints one summary at the end:
  what was done, what was installed, warnings, what failed and what never ran.
  The same summary is saved to ``reports/<script>.txt``.
* ``use_project_venv()`` re-runs the calling script with ``.environment``'s
  Python when it was started with some other interpreter, so
  ``python3 .03_admin.py`` works without activating the environment first.
* ``offer_next()`` asks whether to go straight on to the next numbered script.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR / ".environment"
VENV_PYTHON = ENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
REPORTS_DIR = BASE_DIR / "reports"

# Line-buffer our output so it stays in order with the subprocesses (pip,
# manage.py) that write straight to the terminal.
try:
    sys.stdout.reconfigure(line_buffering=True)
except (AttributeError, ValueError):
    pass

_COLOUR = sys.stdout.isatty()
G, Y, R, B, N = (
    ("\033[32m", "\033[33m", "\033[31m", "\033[1m", "\033[0m") if _COLOUR else ("",) * 5
)


class Abort(Exception):
    """Raised by ``Report.step`` when a critical step fails: stop, then report."""


class Report:
    DONE, INSTALLED, WARN, FAIL, SKIP = "done", "installed", "warn", "fail", "skip"

    def __init__(self, title, slug):
        self.title = title
        self.slug = slug
        self.entries = []          # (kind, label, detail)
        self.started = time.time()
        # Entries recorded before this script re-ran itself under another
        # interpreter (see carry()) — so the final report still lists them.
        carried = os.environ.pop(self._carry_key(), "")
        if carried:
            try:
                saved = json.loads(carried)
                self.entries = [tuple(e) for e in saved["entries"]]
                self.started = saved["started"]
            except (ValueError, KeyError, TypeError):
                pass
        print(f"{B}{title}{N}")
        print(f"  folder : {BASE_DIR}")
        print(f"  python : {sys.executable} ({sys.version.split()[0]})")

    def _carry_key(self):
        return "UCS_REPORT_" + self.slug.upper()

    def carry(self):
        """Hand the entries so far to a re-exec'd copy of this script."""
        os.environ[self._carry_key()] = json.dumps(
            {"entries": self.entries, "started": self.started}
        )

    # -- recording ----------------------------------------------------------
    def _add(self, kind, label, detail, mark):
        self.entries.append((kind, label, detail))
        print(f"  {mark} {label}{' — ' + detail if detail else ''}")

    def done(self, label, detail=""):
        self._add(self.DONE, label, detail, f"{G}[ ok ]{N}")

    def installed(self, label, detail=""):
        self._add(self.INSTALLED, label, detail, f"{G}[inst]{N}")

    def warn(self, label, detail=""):
        self._add(self.WARN, label, detail, f"{Y}[warn]{N}")

    def fail(self, label, detail=""):
        self._add(self.FAIL, label, detail, f"{R}[FAIL]{N}")

    def skip(self, label, detail=""):
        self._add(self.SKIP, label, detail, "[skip]")

    @staticmethod
    def heading(text):
        print(f"\n{B}==> {text}{N}")

    def step(self, label, fn, *args, critical=True, **kwargs):
        """Run ``fn``; record a failure (with the error) if it raises.

        A critical failure raises ``Abort`` so the caller can jump straight to
        ``finish()``; a non-critical one returns None and carries on.
        """
        try:
            return fn(*args, **kwargs)
        except (KeyboardInterrupt, Abort):
            raise
        except BaseException as exc:  # noqa: BLE001 — SystemExit from call_command too
            detail = f"{type(exc).__name__}: {exc}".strip()
            self.fail(label, detail.splitlines()[0][:300])
            if critical:
                raise Abort(label) from exc
            return None

    def task(self, label, fn, *args, detail="", critical=True, **kwargs):
        """``step`` that also records ``label`` as done when it succeeds."""
        failures = sum(1 for kind, _l, _d in self.entries if kind == self.FAIL)
        result = self.step(label, fn, *args, critical=critical, **kwargs)
        if sum(1 for kind, _l, _d in self.entries if kind == self.FAIL) == failures:
            self.done(label, detail)
        return result

    def not_run(self, labels, reason="an earlier step failed"):
        for label in labels:
            self.entries.append((self.SKIP, label, f"not run — {reason}"))

    # -- summary ------------------------------------------------------------
    @property
    def failed(self):
        return any(kind == self.FAIL for kind, _l, _d in self.entries)

    def finish(self, next_hint=None):
        """Print and save the summary. Returns the process exit code."""
        groups = [
            (self.DONE, "Done"),
            (self.INSTALLED, "Installed"),
            (self.WARN, "Warnings"),
            (self.FAIL, "Failed / not installed"),
            (self.SKIP, "Skipped / not run"),
        ]
        elapsed = time.time() - self.started
        lines = ["=" * 72, f"REPORT — {self.title}", "=" * 72]
        for kind, heading in groups:
            items = [(l, d) for k, l, d in self.entries if k == kind]
            if not items:
                continue
            lines.append(f"\n{heading} ({len(items)})")
            lines.extend(f"  • {l}{' — ' + d if d else ''}" for l, d in items)
        lines.append("")
        if self.failed:
            lines.append(f"Finished with problems in {elapsed:.0f}s — see 'Failed' above.")
        else:
            lines.append(f"Finished successfully in {elapsed:.0f}s.")
        if next_hint:
            lines.append(f"Next: {next_hint}")

        text = "\n".join(lines)
        colour = R if self.failed else G
        print("\n" + text.replace(lines[1], f"{B}{colour}{lines[1]}{N}", 1))
        try:
            REPORTS_DIR.mkdir(exist_ok=True)
            path = REPORTS_DIR / f"{self.slug}.txt"
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            path.write_text(f"{stamp}\n{text}\n", encoding="utf-8")
            print(f"\n📝 Report saved to {path.relative_to(BASE_DIR)}")
        except OSError:
            pass
        return 1 if self.failed else 0


def in_project_venv():
    try:
        return Path(sys.prefix).resolve() == ENV_DIR.resolve()
    except OSError:
        return False


def use_project_venv(script):
    """Re-exec *script* with .environment's Python unless already running in it."""
    if in_project_venv():
        return
    if not VENV_PYTHON.exists():
        # A host build (render-build.sh) installs into its own interpreter and
        # has no .environment — carry on there if Django is importable.
        try:
            import django  # noqa: F401
            return
        except ImportError:
            print(
                f"❌ The virtual environment {ENV_DIR.name} does not exist yet.\n"
                "   Run the installer first:  python3 .01_install.py"
            )
            sys.exit(1)
    print(f"↪  Re-running with {VENV_PYTHON.relative_to(BASE_DIR)}\n")
    sys.stdout.flush()
    argv = [str(VENV_PYTHON), str(Path(script).resolve())] + sys.argv[1:]
    if os.name == "nt":
        sys.exit(subprocess.run(argv, check=False).returncode)
    os.execv(str(VENV_PYTHON), argv)


def ask(question, default=False, assume_yes=False):
    if assume_yes:
        return True
    if not sys.stdin or not sys.stdin.isatty():
        return default
    try:
        return input(f"{question} [y/N]: ").strip().lower() in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return default


def offer_next(script, question, extra_args=()):
    """Offer to run the next numbered script; exits with its return code if run.

    Always asks (never auto-answered by --yes): the next script may be
    destructive, and each one is meant to be a deliberate step.
    """
    if not ask(f"\n{question}", default=False):
        print(f"   Run it later with:  python3 {script}")
        return
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    print()
    sys.stdout.flush()
    sys.exit(subprocess.run([python, str(BASE_DIR / script), *extra_args], check=False).returncode)
