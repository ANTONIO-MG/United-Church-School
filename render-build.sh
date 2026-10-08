#!/usr/bin/env bash
#
# Render build command — runs on every deploy, before the new instance starts
# taking traffic. Referenced from ../render.yaml (buildCommand).
#
# Everything here runs with the service's environment variables already set, so
# DATABASE_URL points at the attached PostgreSQL instance and the settings
# module resolves exactly as it will at run time.

set -o errexit   # any failing step fails the deploy, instead of shipping a half-built image
set -o nounset
set -o pipefail

echo "──> Python: $(python --version)"

# ---------------------------------------------------------------------------
# 1. Dependencies
# ---------------------------------------------------------------------------
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# ---------------------------------------------------------------------------
# 2. Static files
#
# Collected into staticfiles/ and compressed by WhiteNoise, which serves them
# from the app process — Render's free tier puts no web server in front of it.
# Must happen before the instance starts or the site loads without CSS.
# ---------------------------------------------------------------------------
python manage.py collectstatic --noinput

# ---------------------------------------------------------------------------
# 3. Database
#
# RUN_DB_WIPE is the one-shot switch for a first deploy: .admin_wipe_and_create.py
# DROPS EVERY TABLE, re-runs the migrations, installs the academic spine and
# creates the four base accounts. --yes skips its "Type 'WIPE' to continue"
# prompt, which nothing can answer in a build container.
#
# ⚠️  It is read on EVERY deploy. Leave it true and every push to this branch
#     destroys all production data — students, marks, uploads, invoices. Set it
#     to true for the first deploy only, then set it back to false in the Render
#     dashboard BEFORE pushing again.
# ---------------------------------------------------------------------------
if [ "${RUN_DB_WIPE:-false}" = "true" ]; then
    echo "══════════════════════════════════════════════════════════════════"
    echo " RUN_DB_WIPE=true — DROPPING ALL TABLES and reseeding from scratch."
    echo " Set RUN_DB_WIPE=false in the Render dashboard after this deploy."
    echo "══════════════════════════════════════════════════════════════════"
    # The script runs makemigrations + migrate itself, so no separate migrate.
    python .admin_wipe_and_create.py --yes
else
    python manage.py migrate --noinput
fi

# ---------------------------------------------------------------------------
# 4. Refuse to ship an unsafe configuration
#
# --deploy turns on the production-only checks (TLS redirect, secure cookies,
# HSTS, Host allow-list) plus this project's own guards in
# apps/diagnostics/deploy_checks.py and apps/finance/checks.py. Failing here
# costs a deploy; failing in production costs rather more.
# ---------------------------------------------------------------------------
python manage.py check --deploy --fail-level ERROR

echo "──> Build complete."
