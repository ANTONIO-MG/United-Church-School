#!/usr/bin/env python3
"""Run the United Church School LMS on this server, bringing the whole stack up with it.

    python3 run.py              # serves on 0.0.0.0:8000
    python3 run.py 8080         # a different port
    PORT=80 python3 run.py      # port via the environment
    python3 run.py --check      # run the preflight only, then exit

Before serving, this starts and verifies everything the app needs:

    1. postgresql   — the service (systemd on Linux; Homebrew / the EDB installer
                      in /Library/PostgreSQL on macOS), then a real Django connection
    2. redis        — only when .env sets USE_REDIS=true: the service, then a real
                      cache + channel-layer round-trip
    3. migrations   — applies anything unapplied
    4. school data  — installs Grade 1 – 12, the CAPS subjects, the 2026 fees,
                      the calendar and the school shop if the database has none
    5. staticfiles  — collectstatic when the directory is missing
    6. media dirs   — created so a first upload / SCORM / H5P import cannot fail

First time on this computer? Run  python3 .02_setup.py  — it creates .environment,
installs the requirements and PostgreSQL, and creates the database from .env.

Serves through gunicorn + the uvicorn ASGI worker — the same stack render.yaml
uses in production — so WebSockets (live chat, notification push) work exactly
as they do when deployed. Static files come from whitenoise inside the app
process; there is no nginx in front.

Binds 0.0.0.0, so the site answers on every address this box has: the VCN
private address, the public address, and localhost.

NOTE — .oraclevcn.com is Oracle's PRIVATE DNS zone. Those names resolve only
from inside the VCN; from the public internet you reach this box by its public
IP address instead.
"""

import os
import socket
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / '.environment' / 'bin' / 'python'
GUNICORN = BASE_DIR / '.environment' / 'bin' / 'gunicorn'

# Host the app is reachable on inside the VCN, echoed in the banner below.
# Set VCN_FQDN in the environment to the instance's internal DNS name.
VCN_FQDN = os.getenv('VCN_FQDN', socket.getfqdn())

# systemd units the app cannot run without (Linux). Enabled at boot, so this is
# a repair step for the case where one died or was stopped by hand. Redis is
# only required when .env turns it on.
REQUIRED_UNITS = ('postgresql', 'redis-server')

# Directories the app writes into at runtime. Absent, the first upload 500s.
RUNTIME_DIRS = ('media', 'media/scorm', 'media/h5p', 'backups/archived_accounts')

OK, BAD = '  ok  ', ' FAIL '


def _fail(message):
    sys.exit(f'run.py: {message}')


def _step(label, ok, detail=''):
    print(f'  [{OK if ok else BAD}] {label:<24} {detail}')
    return ok


def _run_django(snippet):
    """Execute a snippet inside the venv with Django set up.

    Kept as a subprocess rather than an import because run.py itself runs under
    the system python3, which has none of the app's dependencies.
    """
    code = (
        'import os, django\n'
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')\n"
        'django.setup()\n'
    ) + snippet
    return subprocess.run(
        [str(VENV_PYTHON), '-c', code],
        cwd=BASE_DIR, capture_output=True, text=True,
    )


# --------------------------------------------------------------------------
# preflight
# --------------------------------------------------------------------------

def _env_value(key, default=''):
    """A value from .env (run.py runs under the system python, without dotenv)."""
    value = os.getenv(key)
    if value is not None:
        return value
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if line.startswith(f'{key}=') or line.startswith(f'{key} ='):
                value = line.split('=', 1)[1].split(' #', 1)[0].strip().strip('"').strip("'")
    return default if value is None else value


def _redis_wanted():
    return _env_value('USE_REDIS', 'false').lower() in ('1', 'true', 'yes', 'on')


def _tcp_open(host, port):
    try:
        socket.create_connection((host, int(port)), timeout=3).close()
        return True
    except OSError:
        return False


def _start_postgres_macos():
    """Best-effort start of a local PostgreSQL on macOS: Homebrew, then the EDB
    installer's launchd job, then Postgres.app."""
    import glob
    import shutil
    if shutil.which('brew'):
        for formula in ('postgresql@16', 'postgresql@17', 'postgresql@18', 'postgresql'):
            if subprocess.run(['brew', 'services', 'start', formula],
                              capture_output=True).returncode == 0:
                return f'started with brew services ({formula})'
    for data in sorted(glob.glob('/Library/PostgreSQL/*/data'), reverse=True):
        version = Path(data).parent.name
        if subprocess.run(['sudo', '-n', 'launchctl', 'kickstart', '-k',
                           f'system/postgresql-{version}'], capture_output=True).returncode == 0:
            return f'started PostgreSQL {version} (launchd)'
    if Path('/Applications/Postgres.app').exists():
        subprocess.run(['open', '-a', 'Postgres'], capture_output=True)
        return 'opened Postgres.app'
    return ''


def ensure_services_macos():
    """macOS has no systemd: check the database (and Redis) are reachable on
    the host/port in .env, starting a local PostgreSQL if it is down."""
    import time
    host = _env_value('POSTGRES_HOST', '127.0.0.1') or '127.0.0.1'
    port = _env_value('POSTGRES_PORT', '5432') or '5432'
    if _env_value('DATABASE_URL'):
        return _step('postgresql', True, 'DATABASE_URL set — checked by the connection test')
    ok = (Path(host, f'.s.PGSQL.{port}').exists() if host.startswith('/')
          else _tcp_open(host, port))
    if ok:
        _step('postgresql', True, f'answering on {host}:{port}')
    elif host in ('127.0.0.1', 'localhost', '::1'):
        how = _start_postgres_macos()
        for _ in range(15):
            if _tcp_open(host, port):
                break
            time.sleep(1)
        ok = _tcp_open(host, port)
        _step('postgresql', ok, how if ok else 'not running — start PostgreSQL (or run python3 .02_setup.py)')
    else:
        _step('postgresql', False, f'{host}:{port} does not answer')
    if _redis_wanted():
        url = _env_value('REDIS_URL', 'redis://127.0.0.1:6379/0')
        rest = url.split('://', 1)[-1].split('@')[-1].split('/')[0]
        r_host, _, r_port = rest.partition(':')
        r_ok = _tcp_open(r_host or '127.0.0.1', r_port or 6379)
        if not r_ok and r_host in ('127.0.0.1', 'localhost'):
            subprocess.run(['brew', 'services', 'start', 'redis'], capture_output=True)
            r_ok = _tcp_open(r_host, r_port or 6379)
        _step('redis-server', r_ok, f'answering on {r_host}:{r_port or 6379}' if r_ok else
              f'{r_host}:{r_port or 6379} does not answer — start Redis or set USE_REDIS=false in .env')
        ok = ok and r_ok
    return ok


def ensure_units():
    """Start postgresql / redis-server if they are not already running."""
    import shutil
    if not shutil.which('systemctl'):
        return ensure_services_macos()
    all_ok = True
    units = REQUIRED_UNITS if _redis_wanted() else tuple(u for u in REQUIRED_UNITS if u != 'redis-server')
    for unit in units:
        active = subprocess.run(['systemctl', 'is-active', '--quiet', unit]).returncode == 0
        if not active:
            # -n: never prompt. If sudo would ask for a password we want the
            # clear message below rather than a hung, silent start-up.
            started = subprocess.run(
                ['sudo', '-n', 'systemctl', 'start', unit],
                capture_output=True, text=True,
            )
            active = started.returncode == 0
            if not active:
                _step(unit, False, f'could not start — run: sudo systemctl start {unit}')
                all_ok = False
                continue
            _step(unit, True, 'was stopped — started it')
        else:
            _step(unit, True, 'already running')
    return all_ok


def check_database():
    result = _run_django(
        'from django.db import connection\n'
        'connection.ensure_connection()\n'
        'with connection.cursor() as c:\n'
        "    c.execute('select current_database()')\n"
        "    print(c.fetchone()[0])\n"
    )
    detail = result.stdout.strip() or result.stderr.strip().splitlines()[-1:] or ['']
    return _step('database', result.returncode == 0,
                 detail if isinstance(detail, str) else detail[0])


def check_redis():
    """Cache and channel layer both, because they use different Redis DBs.
    (With USE_REDIS off both run in memory and this is a quick sanity check.)"""
    result = _run_django(
        'import asyncio\n'
        'from django.core.cache import cache\n'
        'from channels.layers import get_channel_layer\n'
        "cache.set('__runpy', 'ok', 30)\n"
        "assert cache.get('__runpy') == 'ok', 'cache round-trip failed'\n"
        'layer = get_channel_layer()\n'
        'async def probe():\n'
        "    await layer.send('runpy.probe', {'type': 'ping'})\n"
        "    return await layer.receive('runpy.probe')\n"
        'asyncio.run(probe())\n'
        "print('cache + channel layer')\n"
    )
    detail = result.stdout.strip() or (result.stderr.strip().splitlines() or [''])[-1]
    return _step('redis', result.returncode == 0, detail)


def apply_migrations():
    pending = _run_django(
        'from io import StringIO\n'
        'from django.core.management import call_command\n'
        'out = StringIO()\n'
        "call_command('showmigrations', '--plan', stdout=out)\n"
        "print(sum(1 for line in out.getvalue().splitlines() if line.startswith('[ ]')))\n"
    )
    if pending.returncode != 0:
        return _step('migrations', False, (pending.stderr.strip().splitlines() or [''])[-1])

    count = int(pending.stdout.strip() or 0)
    if not count:
        return _step('migrations', True, 'up to date')

    print(f'  [ .... ] migrations              applying {count}…')
    applied = subprocess.run(
        [str(VENV_PYTHON), 'manage.py', 'migrate', '--noinput'],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    return _step('migrations', applied.returncode == 0,
                 f'applied {count}' if applied.returncode == 0
                 else (applied.stderr.strip().splitlines() or [''])[-1])


def ensure_school_data():
    """The school structure and shop are reference data the app expects — seed
    them (non-destructively) when a fresh database has none."""
    result = _run_django(
        'from apps.learning.models import Programme\n'
        "print(Programme.objects.filter(institution__code='UCS').count())\n"
    )
    if result.returncode != 0:
        return _step('school data', False, (result.stderr.strip().splitlines() or [''])[-1])
    grades = int(result.stdout.strip() or 0)
    if grades:
        return _step('school data', True, f'{grades} grades')
    print('  [ .... ] school data             installing Grade 1 – 12, subjects, fees, shop…')
    seeded = all(subprocess.run([str(VENV_PYTHON), 'manage.py', *command], cwd=BASE_DIR,
                                capture_output=True, text=True).returncode == 0
                 for command in (['seed_school_structure', '--verbosity', '0'],
                                 ['seed_shop', '--quiet']))
    return _step('school data', seeded, 'installed' if seeded
                 else 'seeding failed — run: python manage.py seed_school_structure')


def ensure_static():
    """whitenoise serves whatever is in staticfiles/, so a missing directory
    shows up as unstyled pages rather than an error — collect it once."""
    if (BASE_DIR / 'staticfiles').is_dir():
        return _step('static files', True, 'present')
    print('  [ .... ] static files            collecting…')
    collected = subprocess.run(
        [str(VENV_PYTHON), 'manage.py', 'collectstatic', '--noinput'],
        cwd=BASE_DIR, capture_output=True, text=True,
    )
    return _step('static files', collected.returncode == 0,
                 'collected' if collected.returncode == 0 else 'collectstatic failed')


def ensure_runtime_dirs():
    for rel in RUNTIME_DIRS:
        (BASE_DIR / rel).mkdir(parents=True, exist_ok=True)
    return _step('media dirs', True, 'present')


def check_port(host, port):
    """Catch a port clash here, with the likely cause, instead of letting
    gunicorn die on bind with a bare EADDRINUSE."""
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        probe.bind((host, int(port)))
        return _step(f'port {port}', True, 'free')
    except OSError as exc:
        hint = ''
        if port in ('80', '443'):
            hint = ' — the systemd unit serves :80 (sudo systemctl stop ucs-lms)'
        return _step(f'port {port}', False, f'{exc.strerror}{hint}')
    finally:
        probe.close()


def preflight(host, port):
    print('\n  Preflight')
    results = [
        ensure_units(),
        check_database(),
        check_redis(),
        apply_migrations(),
        ensure_school_data(),
        ensure_static(),
        ensure_runtime_dirs(),
        check_port(host, port),
    ]
    return all(results)


# --------------------------------------------------------------------------
# banner
# --------------------------------------------------------------------------

def _local_ips():
    """Addresses this box answers on, best-effort, for the banner."""
    ips = set()
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(('8.8.8.8', 80))  # UDP: selects the outward interface, sends nothing
        ips.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith('127.'))


def _public_ip():
    """The address the public internet reaches this box on.

    The VNIC metadata does not carry one (the public address is mapped upstream
    of the instance), so ask an outside echo service and keep the timeout short
    — this is banner text, never a reason to delay start-up.
    """
    import urllib.request
    try:
        with urllib.request.urlopen('https://api.ipify.org', timeout=3) as response:
            return response.read().decode().strip()
    except Exception:
        return ''


def banner(port):
    print()
    print('  United Church School LMS')
    print(f'  This machine  : http://127.0.0.1:{port}')
    for ip in _local_ips():
        print(f'  On the VCN    : http://{ip}:{port}')
    print(f'  By VCN name   : http://{VCN_FQDN}:{port}   (inside the VCN only)')
    public = _public_ip()
    if public:
        print(f'  On the internet: http://{public}:{port}')
        print(f'  Landing page  : http://{public}:{port}/social/landing/')
    print('  Admin         : add /admin/ to any of the above')
    print()
    print('  Ctrl-C to stop.')
    print()


def main():
    if not GUNICORN.exists():
        _fail(
            f'{GUNICORN} not found.\n'
            '       The virtualenv is .environment — set this computer up first:\n'
            '         python3 .02_setup.py\n'
            '       (or by hand: python3.12 -m venv .environment &&\n'
            '         .environment/bin/python -m pip install -r requirements.txt)'
        )

    args = [a for a in sys.argv[1:] if a != '--check']
    check_only = '--check' in sys.argv[1:]

    port = os.getenv('PORT') or (args[0] if args else '8000')
    host = os.getenv('HOST', '0.0.0.0')

    if port == '80' and hasattr(os, 'geteuid') and os.geteuid() != 0:
        # The systemd unit already serves :80 with CAP_NET_BIND_SERVICE; a bare
        # run.py has no such capability and would die with EACCES.
        _fail(
            'port 80 needs privileges this process does not have.\n'
            '       Port 80 is already served by the systemd unit:\n'
            '         sudo systemctl status ucs-lms\n'
            '       Use the default port instead:  python3 run.py'
        )

    if not preflight(host, port):
        _fail('preflight failed — see the FAIL lines above. Nothing was started.')

    if check_only:
        print('\n  Preflight passed. (--check: not serving.)\n')
        return

    banner(port)

    # execv replaces this process image immediately; when stdout is a file or a
    # pipe (nohup, systemd, a log redirect) it is block-buffered, and everything
    # printed above would be discarded unflushed. Push it out first.
    sys.stdout.flush()
    sys.stderr.flush()

    os.execv(str(GUNICORN), [
        str(GUNICORN),
        'config.asgi:application',
        '--worker-class', 'uvicorn_worker.UvicornWorker',
        '--workers', '1',
        '--bind', f'{host}:{port}',
        '--access-logfile', '-',
        '--error-logfile', '-',
    ])


if __name__ == '__main__':
    main()
