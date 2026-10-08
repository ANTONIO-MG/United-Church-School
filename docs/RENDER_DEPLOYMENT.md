# Deploying to Render (free tier)

Everything the platform needs is in the repository: [`render.yaml`](../../render.yaml)
at the repository root (the Blueprint: web service + PostgreSQL) and
[`render-build.sh`](../render-build.sh) next to `manage.py` (the build).

The short version: push the repo, create a Blueprint from it, set `RUN_DB_WIPE`
to `true` for the first deploy, then set it back to `false`.

---

## 0. How configuration resolves in production

Worth understanding before anything else, because this repository is unusual on
one point: **`.env` is committed** (see the note in `.gitignore`), so it travels
to Render carrying development values — `DEBUG=True`, `ALLOWED_HOSTS=*`, a
`127.0.0.1` database.

That is safe because of the order things load, and nothing in `.env` needs to
change:

1. Render sets the service's environment variables.
2. `load_dotenv()` fills in **only what is still missing** — it never overwrites
   what Render set.
3. `config/settings.py` snapshots the platform's variables *before* step 2
   (`PROCESS_ENV`) so it can still tell the two apart afterwards. Settings that
   are dangerous to inherit from a developer's `.env` are decided by the
   platform: `DEBUG` (off), `ALLOWED_HOSTS` (the Render hostname, wildcard
   dropped), `SESSION_COOKIE_SECURE` (on), `SITE_URL` (the real public URL).

So: **set production values in the Render dashboard, never in `.env`.**

---

## 1. Locally, before you deploy

Run from the project root (`United-Church-School/`) with the virtualenv active.

```bash
# Dependencies (now includes gunicorn, uvicorn and whitenoise)
python -m pip install -r requirements.txt

# The production checks — the same ones the build runs.
# Simulates a Render environment so the production branches are the ones tested.
RENDER=true \
RENDER_EXTERNAL_HOSTNAME=ucs-lms.onrender.com \
DATABASE_URL='postgresql://postgres:PASSWORD@127.0.0.1:5432/united_church_school_db?sslmode=disable' \
SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key as k; print(k())')" \
python manage.py check --deploy --fail-level ERROR

# Optional: serve the real production stack locally and click around.
# (SECURE_SSL_REDIRECT=false only because this test is over plain HTTP.)
RENDER=true RENDER_EXTERNAL_HOSTNAME=localhost:8099 SECURE_SSL_REDIRECT=false \
DATABASE_URL='postgresql://postgres:PASSWORD@127.0.0.1:5432/united_church_school_db?sslmode=disable' \
SECRET_KEY='local-smoke-test-key' \
gunicorn config.asgi:application \
  --worker-class uvicorn_worker.UvicornWorker --bind 127.0.0.1:8099 --workers 1
# → http://127.0.0.1:8099/
```

Then commit and push — Render deploys from GitHub, not from your disk:

```bash
git add -A && git commit -m "Deploy configuration for Render"
git push origin main
```

---

## 2. Create the service on Render

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**.
2. Connect the GitHub repository and pick the branch (`main`).
3. Render reads `render.yaml` and offers two resources — the web service
   `ucs-lms` and the database `ucs-lms-db`. Apply.

It wires `DATABASE_URL` to the database, generates a `SECRET_KEY`, and starts
the first build. No environment variables to type in by hand.

The first build should go green: `migrate` creates the schema in the empty
database. But the site has **no accounts and no academic structure** yet, and
the free tier gives you no shell to run `createsuperuser` in — so there is no
way to log in. That is what step 3 is for.

---

## 3. First deploy: build the database

`.admin_wipe_and_create.py` drops every table, re-runs the migrations, installs
the academic spine (institutions, programmes, modules, cohorts, calendars) and
creates the four base accounts. `render-build.sh` runs it with `--yes`, which
skips the interactive `Type 'WIPE' to continue:` prompt that nothing could
answer inside a build container.

1. Web service → **Environment** → set `RUN_DB_WIPE` to `true` → **Save**.
   (Saving triggers a deploy.)
2. Watch **Logs**. You want:
   `RUN_DB_WIPE=true — DROPPING ALL TABLES and reseeding from scratch.`
   then the eight `[n/8]` steps, then `Build complete.`
3. **Immediately set `RUN_DB_WIPE` back to `false`** and save.

> ⚠️ `RUN_DB_WIPE` is read on **every** deploy. Left at `true`, every push to
> `main` destroys everything in the database — students, marks, uploads,
> invoices, payments — with no backup taken. There is no confirmation prompt;
> that is what you asked the build for.

Sign in at `https://<your-service>.onrender.com/` with any of the four accounts
(all on password `Password@99` — change them):

| Account | Role |
| --- | --- |
| `admin@ucs.org.za` | superuser, `/admin/` |
| `educator@ucs.org.za` | educator |
| `student@ucs.org.za` | student |
| `parent@ucs.org.za` | parent, linked to the student |

To add the demonstration data as well, set `RUN_DB_WIPE=true` again and add
`python .demo_seed.py` to `render-build.sh` — the seed assumes the wipe has just
run.

---

## 4. After the first deploy

**Google sign-in** — the button 500s until the Render URL is a registered
redirect URI. Google Cloud Console → Credentials → your OAuth client → add:

```
https://<your-service>.onrender.com/accounts/google/login/callback/
```

See [google-oauth-setup.md](google-oauth-setup.md).

**E-mail** already works: the SMTP credentials are in the committed `.env`.
Verification links now point at the Render URL, because `SITE_URL` follows the
platform hostname.

**Payments are off.** `PAYMENTS_ENABLED=false` in the Blueprint. PayFast is
unconfigured, and `apps/finance/checks.py` refuses to start a production build
that is either pointed at the sandbox or live with no merchant credentials —
both states take money that never arrives. The pay page says online payment is
unavailable and the invoice stays due, instead of building a checkout that dies
at PayFast. To turn it on: set `PAYFAST_MERCHANT_ID`, `PAYFAST_MERCHANT_KEY`,
`PAYFAST_PASSPHRASE`, `PAYFAST_SANDBOX=false` and `PAYMENTS_ENABLED=true`.

**Connect to the database from your laptop** — the `DATABASE_URL` on the service
is Render's *internal* address and does not resolve outside their network. Take
the **External Database URL** from the database's dashboard page and put it in
your local `.env` as `DATABASE_PUBLIC_URL`; settings prefer it off-platform.

```bash
psql "$EXTERNAL_DATABASE_URL"                 # inspect
pg_dump "$EXTERNAL_DATABASE_URL" > backup.sql # back up (do this before day 30)
```

---

## 5. What the free tier costs you

| Limit | Consequence |
| --- | --- |
| Service sleeps after 15 min idle | First request after that waits ~50 s. Open WebSockets (chat, notification push) drop when it sleeps. |
| **Free database expires after 30 days** | Everything in it goes. `pg_dump` before then, or upgrade the instance. |
| Ephemeral filesystem | Uploads — avatars, course covers, chat attachments — are destroyed on every deploy and restart. Set `FILE_SERVER_BACKEND=s3` with the `AWS_*` credentials to keep them. |
| 512 MB RAM, one worker | Set in the start command, and not only for memory: with `USE_REDIS=false` the Channels layer is in-process, so a second worker would be a second, disconnected chat bus. Raise both together. |
| No shell on free instances | Anything you would run by hand goes in `render-build.sh`, guarded by an environment variable — as `RUN_DB_WIPE` is. |

---

## 6. Troubleshooting

| Symptom | Cause |
| --- | --- |
| Build fails: `deploy.E001/E002` (ALLOWED_HOSTS) | `RENDER_EXTERNAL_HOSTNAME` was not set — only true outside a Render service. |
| Build fails: `finance.E001/E002` | `PAYMENTS_ENABLED` was set to `true` without full PayFast credentials. |
| Build fails: `ImproperlyConfigured: … loopback address` | The database is not attached; `DATABASE_URL` is missing, so settings fell back to the committed `.env`'s `127.0.0.1`. |
| Site loads with no CSS | `collectstatic` did not run, or WhiteNoise is not in `MIDDLEWARE` right after `SecurityMiddleware`. |
| Every POST fails CSRF (`Origin checking failed`) | The public origin is missing from `CSRF_TRUSTED_ORIGINS` — normally automatic from `RENDER_EXTERNAL_HOSTNAME`. |
| Redirect loop | `SECURE_SSL_REDIRECT` on without `SECURE_PROXY_SSL_HEADER`; on a platform it is set automatically, so check `USE_X_FORWARDED_PROTO` has not been forced to `false`. |
| Chat connects then dies | More than one worker with `USE_REDIS=false`. |
| Images 404 after a deploy | Expected on an ephemeral filesystem — see the table above. |
