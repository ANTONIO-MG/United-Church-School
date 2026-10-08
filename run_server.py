#!/usr/bin/env python
"""run_server.py — start the United Church School LMS dev server for the whole network.

Binds Django's runserver to 0.0.0.0 so any phone / laptop on the SAME Wi-Fi or
LAN can reach the hub, and prints the exact address(es) to share.

    python run_server.py                # serves on port 8000
    python run_server.py 9000           # serves on a different port
    HOST=0.0.0.0 PORT=8000 python run_server.py

Anyone on the network then opens  http://<your-computer-ip>:8000  in a browser.
Multiple people can be signed in at once (each device keeps its own session);
to use two different accounts on ONE computer, open a second browser or an
Incognito/Private window.

First time on a machine:
    1) python3 .01_install.py     # Python, .environment, requirements
    2) python3 .02_setup.py       # PostgreSQL, database, school structure and shop
    3) python3 .03_admin.py       # (DESTRUCTIVE) the five base accounts
    4) python3 .04_demo_seed.py   # (optional) demo data
    5) python run_server.py       # start serving the LAN
"""
import os
import socket
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def lan_ips():
    ips = []
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(('8.8.8.8', 80))     # UDP: no packets sent, just picks the interface
        ips.append(probe.getsockname()[0])
        probe.close()
    except Exception:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ip = info[4][0]
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
    except Exception:
        pass
    return ips


def ensure_runtime_dirs():
    """Make sure the folders the app writes to exist, so a first upload / SCORM /
    H5P import doesn't fail on a fresh checkout."""
    for rel in ('media', 'media/scorm', 'media/h5p', 'backups/archived_accounts'):
        (BASE_DIR / rel).mkdir(parents=True, exist_ok=True)


def asgi_status():
    """Whether WebSockets/real-time will be served.

    ``daphne`` is first in INSTALLED_APPS, so once it (and ``channels``) are
    installed Django's ``runserver`` is replaced by Channels' ASGI dev server —
    the same ``manage.py runserver`` then serves HTTP **and** WebSockets, in
    development, with DEBUG=True. If the packages are missing we say so instead of
    letting the server crash on start-up.
    """
    try:
        import channels  # noqa: F401
        import daphne  # noqa: F401
        return True, 'ON — live chat, notification/message sounds & lesson presence (Daphne ASGI)'
    except Exception:
        return False, ("OFF — run `pip install -r requirements.txt` to enable "
                       "(channels + daphne). Without them the server will not start.")


def main():
    host = os.getenv('HOST', '0.0.0.0')
    port = os.getenv('PORT') or (sys.argv[1] if len(sys.argv) > 1 else '8000')

    ensure_runtime_dirs()
    ips = lan_ips()
    bar = '=' * 60
    print('\n' + bar)
    print(' United Church School LMS is starting for your whole network')
    print(bar)
    print(f'  This computer : http://127.0.0.1:{port}')
    for ip in ips:
        print(f'  On the network: http://{ip}:{port}   <- share this')
    if not ips:
        print('  (could not detect a LAN IP — check your Wi-Fi/network)')
    print(bar)
    print('  • Anyone on the same Wi-Fi/LAN can open the network address.')
    print('  • Everyone can be signed in at the same time (one session each).')
    print('  • Two accounts on ONE computer: use a 2nd browser or Incognito.')
    print('  • Stop the server with Ctrl+C.')
    ws_ok, ws_msg = asgi_status()
    print(f'  • Real-time (WebSockets): {ws_msg}')
    if not ws_ok:
        print('    ↳ tip: `pip install -r requirements.txt` then re-run this.')
    print(bar + '\n')
    sys.stdout.flush()

    manage = BASE_DIR / 'manage.py'
    try:
        subprocess.run([sys.executable, str(manage), 'runserver', f'{host}:{port}'], check=False)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
