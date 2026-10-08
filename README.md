<div align="center">

<img src="static/images/brand/ucs-logo.png" alt="United Church School" height="96">

# United Church School — Learning Platform

### United We Stand

**The online home of United Church School (UCS)**, an independent, non-denominational,
co-educational Grade 1 – 12 school in Yeoville, Johannesburg. Learners, parents, teachers and the
school office share one platform for classes, lessons, homework, marks, school fees and admissions.

[🌐 www.ucs.org.za](https://www.ucs.org.za) · [✉️ uchs@unitedcs.co.za](mailto:uchs@unitedcs.co.za) · 📞 011 648 4727 · 📍 44 Frances Street, Yeoville, Johannesburg 2198

<sub>Built with Django 6 · PostgreSQL · Redis · Channels · HTMX · Bootstrap 5 · PayFast · Microsoft Teams · optional Claude AI</sub>

</div>

---

## 🎯 What it is

The UCS learning platform puts the school day online in one place. It follows the **CAPS** curriculum
from **Grade 1 to Grade 12**: each grade carries its subjects, each subject carries its schedule for
the year (terms, weeks, lessons, worksheets, tests and exams), and every learner, parent and teacher
sees exactly what belongs to them.

- 🎓 **Learning**: block-built lessons, a subject schedule per grade, worksheets and study guides,
  quizzes, class tests and exams with auto-marking and rubric-assisted marking, weighted marks, report
  cards and certificates.
- 👨‍👩‍👧 **Parents**: follow a child's progress, marks, notices and calendar; view and pay school-fee
  invoices.
- 🧑🏽‍🏫 **Teachers**: build subject schedules, author lessons and assessments, mark, run live online
  classes (Microsoft Teams) and nudge learners who have gone quiet.
- 🏫 **The school office**: admissions and applications, enrolment, fees and invoicing, the school
  calendar, announcements, analytics, backups and diagnostics.
- 🤝 **Community**: messages, class and subject chats, a social feed, discussions, notifications
  (bell, e-mail and WhatsApp) and a searchable help centre.

## 👥 Who uses it

| Role | Sees / can do |
|------|---------------|
| **Learner** | Their grade and its subjects, the schedule, lessons, homework/tasks, tests, marks, attendance, messages and the school calendar. Learner↔learner DMs need an accepted connection. Can invite up to two parents. |
| **Parent / Guardian** | Their child's progress, marks, notices and calendar; school-fee invoices to **view and pay**. |
| **Teacher (educator)** | **Teach-only**: their subjects, the subject schedule, lessons, assessments, the marking queue, live classes, class registers and nudges. |
| **Staff / Admin** | **Full CRUD** across the school: admissions, grades and subjects, enrolment, invoicing, announcements, analytics, backups, diagnostics and the advanced Claude assistant. |

---

## 🏫 The academic structure

The platform keeps a generic academic spine in code and presents it in school terms:

| In the code | At UCS | Example |
|---|---|---|
| `Institution` | the school | `UCS`: United Church School |
| `Programme` | a grade | `GR01` … `GR12` (Grade 1 … Grade 12) |
| `ProgrammeModule` | a subject offered in that grade | Grade 10 Mathematics, English Home Language, Life Orientation … |
| `Cohort` | a class / year group | `10A`, `2026` |
| `Topic`, `SchedulePhase`, `ScheduleWeek` | the subject's topics, terms and weeks | Term 1 · Week 3 · Functions |

Use the grade (programme) and subject (module) codes for the management commands that filter by them
(e.g. `--institution UCS --programme GR10`). School details, grades, subjects and the 2026 fee schedule
live in `core/school.py` and `core/academic_spine.py`.

## 📝 Admissions, registration & fees

The online application replaces the paper *UCS Application Form 2026* (the PDF is still linked
from the landing page, `static/documents/`). A parent or guardian creates an account and works
through a **five-step wizard** (`/community/register/`):

| Step | What is captured | Form page |
|---|---|---|
| 1 · Learner | name, gender, date of birth, photo, contact number, POPIA consent | — |
| 2 · Grade & subjects | grade applied for, new or current learner; Grade 10 – 12 choose one FAL, Maths or Maths Literacy, and three electives (compulsory subjects come with the grade) | p. 10 |
| 3 · Family | ID / birth certificate / passport / asylum document, study permit, home language, previous school, who the learner lives with, who pays the fees, siblings at UCS, SMSWEB number, father / mother / guardian, emergency contact | p. 2 |
| 4 · Medical & documents | medical conditions, medication, medical aid, doctor, who pays medical costs; uploads: learner photo, birth certificate or ID, clinic card (Gr 1 – 3), study permit, report card, transfer card, parent ID, payslip | p. 1, 3 – 5 |
| 5 · Agreements & fees | terms & conditions, indemnity, extra-murals, both codes of conduct, prospectus, fees & affordability, POPIA, media consent, receipt of documents, typed signature (IP + time stamped); fees due now | p. 6 – 16 |

**Fees on enrolment** come from the grade's fee schedule (`Programme.registration_fee`,
`annual_levy`, `monthly_fee`, seeded from `core/school.py`): registration (new learners only,
non-refundable) + the annual levy + the first month's school fees, with the 5% sibling discount on
school fees. The family pays now (**PayFast**) or by **EFT / card at the school office** — "the
application is pending until payment is received".

| 2026 | Registration | Levy | Monthly (Jan – Dec) | Year incl. levy |
|---|---|---|---|---|
| Grade 1 – 3 | R550 | R1 900 | R1 200 | R16 300 |
| Grade 4 – 6 | R550 | R1 900 | R1 250 | R16 900 |
| Grade 7 – 10 | R550 | R2 200 | R1 800 | R23 800 |
| Grade 11 | R550 | R2 200 | R2 200 | R28 600 |
| Grade 12 | — | R2 200 | R2 750 | R35 200 |

**After submitting**: parents with an e-mail address are invited to a linked parent account; the
family follows the application, uploads missing documents and pays under **My application**
(`/admissions/my-application/`). Paying the invoice unlocks every subject in the grade for the month
and moves the application to the office. When a month lapses, opening a locked subject raises that
month's school-fees invoice (one invoice for the whole grade); the office can also record an EFT /
card payment and grant months from Finance.

**The school office** works applications at **Admissions** (`/admissions/office/`): filters by
status and grade, every detail the family entered, document verification, the page-1 *office use
only* checklist (ACC No, Pastel account, SMSWEB, SA-SAMS learner profile, transfer card received,
registrar sign-off) and the deputy's admit / decline decision. Applications move
*Draft → Submitted (pending payment) / Documents outstanding → Under review → Admitted / Declined*.

**School shop** (`seed_shop`): UCS golf shirts (Primary R270, High School R290, with sizes), tie,
cap and badge (R160), blazer buttons (R5), blazers (R700 – R1 100 by size), mask (R60), and the
additional fees: report reprint (R90), drug test (R90), LRC badge replacement (R50).

---

## ✨ Features

<details open>
<summary><b>🎓 Learning & assessment</b></summary>

- **Subject schedule**: each subject's year as drop-downs (overview & study guide → the weeks of
  each term → tests and exams), with materials and PDFs beside every week. The teaching order
  (guide → questions → answers) is enforced server-side, so answers open only after an attempt.
- **Block-based lesson builder**: headings, rich text, images, audio/video, tables, callouts,
  embedded quizzes and live sessions; autosave; publish to a subject, class or named learners.
- **Assessments**: quizzes, class tests and exams with a full take-engine (sections, resume, timer,
  attempt limits). Questions are auto-marked or marked against a rubric in the marking queue, with an
  optional Claude suggestion the teacher confirms.
- **Content import**: draft lessons and papers from uploaded PDFs/Word/Excel through Claude (always
  saved as drafts for a teacher to review), or import validated JSON content packs.
- **Marks, report cards & certificates**: weighted components, custom letter scales, class
  positions, printable report cards and subject/grade certificates.
</details>

<details>
<summary><b>📅 Calendar & live classes</b></summary>

- **School calendar** (`/calendar/`): live classes, the school's terms, tests and exams, tasks,
  lessons and personal reminders, scoped to each viewer.
- **Calendar export & import**: a private `.ics` feed for Google / Outlook / Apple, and import of
  a personal calendar so free-slot finding respects real commitments.
- **Microsoft Teams**: scheduling a class creates the Teams meeting, invites the right people,
  hands learners in through an identified launch page, pulls attendance, files recordings to
  OneDrive and (optionally) drafts a Claude follow-up pack. See `docs/LIVE_SESSIONS.md` and
  `docs/TEAMS_INTEGRATION.md`.
</details>

<details>
<summary><b>🤝 Communication</b></summary>

- 1:1, class and subject chats with attachments, @mentions, typing indicators and unread badges
  (Django Channels).
- Announcements and broadcasts to the school, a grade, a class, a subject or individuals.
- Notifications on the bell, by e-mail and on **WhatsApp** (with a small reply bot: `WEEK`, `DATES`,
  `SUBJECTS`, `INVOICE`, `NOTICES`, `STOP`).
- A social feed, discussions, Jitsi meeting rooms and a role-scoped **help centre**.
</details>

<details>
<summary><b>💳 Fees, shop & operations</b></summary>

- **Finance**: invoices and estimates, PayFast checkout (signed redirect + ITN), EFT proof of
  payment, receipts, statements, expenses and income reports by grade.
- **School shop**: uniform and school supplies, downloads and 1-on-1 bookings, with courier
  delivery or collection.
- **Tasks**: assignable homework and work items with progress tracking.
- **Staff desk**: teaching and operations dashboards, nudges, academic structure management,
  scheduled database **backups** (`ucs-*.dump`) and restore.
- **Diagnostics**: every error carries a catalogued code (`docs/ERROR_CODES.md`) with a
  user-facing fix and a developer hint.
- **Background jobs**: one `run_scheduled_jobs` command driven by systemd timers, cron or launchd
  (`deploy/scheduler/`).
</details>

<details>
<summary><b>🧠 AI (optional)</b></summary>

- **Admin analytics assistant** (admin/staff): a Claude chat grounded in the live analytics
  snapshot. It stays off until `ANTHROPIC_API_KEY` and `ADMIN_AI_ENABLED` are set.
- **Authoring help**: PDF → draft lesson / assessment, rubric-assisted marking suggestions and
  live-class follow-up packs. The AI never publishes or marks on its own.
</details>

---

## 🚀 Getting started

### 🆕 A new computer: `bash .setup`

```bash
cd United-Church-School
bash .setup            # everything below, checked step by step
bash .setup --demo     # …and load demo learners, teachers and parents
bash .setup --check    # only verify an existing setup
bash .setup --reset    # ⚠️ wipe the database and rebuild it
```

`.setup` (macOS with Homebrew / the EDB PostgreSQL installer / Postgres.app, or Debian/Ubuntu):

1. checks `.env` (all database settings are read from it);
2. finds Python 3.12+ (installs it if missing);
3. creates and activates the virtual environment **`.environment`**;
4. installs `requirements.txt` into it (falls back to `.install_requirements.py` package by package);
5. finds PostgreSQL, or installs it when the `.env` database is on this computer, and starts it;
6. creates the database user and database named in `.env` (`POSTGRES_DB=united_church_school_db`,
   `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, or `DATABASE_URL`) —
   with the EDB installer it asks once for the `postgres` administrator password (or reads
   `POSTGRES_ADMIN_PASSWORD`) if the `.env` user does not exist yet;
7. checks Redis when `USE_REDIS=true`;
8. migrates, installs the school structure (`seed_school_structure`) and the shop (`seed_shop`),
   collects static files, and offers to create the four base accounts;
9. verifies the environment, the database connection, migrations, the school data and the landing
   page, and prints how to start the app.

It is safe to run again — every step checks first and only does what is missing.

> **Redis:** with `USE_REDIS=true` the app needs the Redis at `REDIS_URL`. On a single computer
> without Redis set `USE_REDIS=false` in `.env` (the cache and live channels then run in memory).

### ▶️ Running it

```bash
source .environment/bin/activate
python run.py               # preflight (database, Redis, migrations, school data, static) then serve :8000
python run.py --check       # the preflight only
python run_server.py        # dev server for your whole network (prints the address to share)
python manage.py runserver  # the classic single-machine form
```

Landing page: `/social/landing/` · Django admin: `/admin/`.

### 🔧 By hand

```bash
python3.12 -m venv .environment && source .environment/bin/activate
pip install -r requirements.txt            # or: python .install_requirements.py
# create the PostgreSQL database and user named in .env, then:
python manage.py migrate
python manage.py seed_school_structure     # Grade 1 – 12, CAPS subjects, 2026 fees, calendar
python manage.py seed_shop                 # uniform + additional fees
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### ⚡ Reset with base accounts (dev)

⚠️ **Destructive** — drops and rebuilds every table in the `.env` database:

```bash
python .admin_wipe_and_create.py    # wipe → migrate → school, grades, subjects, fees, shop + base accounts
```

The base accounts (all verified, password `Password@99`) are `admin@ucs.org.za` (superuser),
`educator@ucs.org.za`, `student@ucs.org.za` (a Grade 10 learner with an admitted application) and
`parent@ucs.org.za` (linked to the learner).

### 🎭 Demo data

`.demo_seed.py` fills a running instance with a realistic dataset. It is **non-destructive**, safe
to re-run, and `--wipe` removes it again.

```bash
python .demo_seed.py         # seed learners, teachers and graded activity
python .demo_seed.py --wipe  # remove all of it
```

### 🌐 Running it for the network

```bash
python run_server.py            # binds 0.0.0.0:8000 and prints the URL(s) to share
python run_server.py 9000       # a different port
```

From other devices, open `http://<your-computer-ip>:8000`. The app trusts the machine's LAN IP as a
CSRF origin; behind a proxy/hostname add it to `CSRF_TRUSTED_ORIGINS`. For anything reachable beyond
the LAN, set a real `SECRET_KEY`, a specific `ALLOWED_HOSTS` (e.g. `ucs.org.za,www.ucs.org.za`),
`DEBUG=False`, and serve behind HTTPS.

### 🖥️ Production server

`run.py` brings the whole stack up on the server (PostgreSQL, Redis, gunicorn/uvicorn). The systemd
units live in `deploy/`:

- `deploy/server/ucs-lms.service`: the web app (`sudo systemctl enable --now ucs-lms`)
- `deploy/scheduler/production/ucs-lms-scheduler{,-quick}.{service,timer}`: background jobs
- `deploy/scheduler/za.org.ucs.scheduler.plist`: the macOS (launchd) equivalent

See `deploy/server/README.md`, `deploy/scheduler/README.md` and `docs/RENDER_DEPLOYMENT.md`.

---

## 🔌 External services

`pip install` only fetches the libraries. These are wired through `.env`:

| # | Service | Needed? | What for |
|---|---------|---------|----------|
| 1 | 🐘 **PostgreSQL** | ✅ **Required** | Primary database (`POSTGRES_*`) |
| 2 | 🐬 MySQL | ➖ Optional | DR/backup replica (`MYSQL_*`) |
| 3 | 🧰 Redis | ➖ Recommended | Cache, Channels layer and Celery broker |
| 4 | ✉️ **SMTP** | ✅ for real e-mail | Verification, resets, notifications (`EMAIL_*`) |
| 5 | 🔐 Google OAuth | ➖ Optional | "Continue with Google" (`docs/google-oauth-setup.md`) |
| 6 | 🎥 Microsoft Graph | ➖ Optional | Teams meetings, attendance, OneDrive (`MS_GRAPH_*`) |
| 7 | 💬 WhatsApp Cloud API | ➖ Optional | WhatsApp notifications and the reply bot |
| 8 | 💳 **PayFast** | ➖ Optional | Online school-fee payments (`PAYFAST_*`); sandbox by default |
| 9 | ✨ Anthropic (Claude) | ➖ Optional | AI authoring help and the admin assistant (`ANTHROPIC_API_KEY`) |

---

## 🧱 Architecture

- **Django 6** project; settings module `config.settings`; each domain is its own app under
  `apps/*` with business logic in services, not views.
- **PostgreSQL** primary, optional **MySQL** DR replica (a DB router keeps the copy in sync).
- **Templates** live in the root `templates/<app>/`; every signed-in page extends one chrome
  (`templates/myhub/elements/layouts/admin.html`), and HTMX swaps page bodies (`docs/HTMX.md`).
- **Real-time** via Django Channels (`docs/WEBSOCKETS.md`).
- **Auth** via `django-allauth` (e-mail login, verification, reset, Google), with site-wide login,
  enforced onboarding and management-only URL gates in middleware.
- **DRF** REST API under `/api/…`.

### App map

```
apps/accounts       identity, profiles, registration wizard, parent links, invitations, audit log
apps/admissions     the UCS application for admission (learner, guardians, medical, consents, documents)
apps/myhub          dashboard, landing page, search, social feed
apps/learning       grades & subjects (the academic spine), schedules, lessons, enrolment & unlocking
apps/assessments    quizzes/tests/exams, take-engine, auto + rubric marking, weighting
apps/reports        marks, letter scales, report cards, certificates, class positions
apps/analytics      academic intelligence & risk monitoring
apps/livesessions   the school calendar, live classes, calendar feeds & imports
apps/msteams        Microsoft Graph: Teams meetings, attendance, recordings, OneDrive
apps/communication  chat, mail, notifications, announcements, broadcasts, WhatsApp, help centre, e-mails
apps/finance        invoices, PayFast, proof of payment, receipts, statements, expenses, reports
apps/shop           school shop, cart, downloads, bookings, courier
apps/tasks          assignable tasks/homework with progress
apps/staffdesk      staff dashboards, nudges, academic admin, backups
apps/revision       revision tools
apps/diagnostics    the error-code catalogue and deploy checks
apps/scheduler      background jobs (run_scheduled_jobs)
apps/ai_assistant   Claude authoring help + the admin analytics assistant
```

---

## 🎨 Branding & copy: one file

The school's name, crest, contacts, banking details, social links and all static UI text live in
**`.strings.json`** (project root), loaded by `core/branding.py` and exposed to every template as
`brand` / `org` / `site`. In Python, read it with `from core.branding import BRAND, t`. **Never
hard-code user-facing text**: add a key and read it with `t()` / the `org_brand` tag. Brand images
are in `static/images/brand/` (`ucs-logo.png`, `ucs-logo-white.png`, `ucs-mark.png`, `ucs-crest.png`).

---

## 🗂️ Repository layout

```
United-Church-School/
├── README.md · NEW_FEATURES.md
├── manage.py · requirements.txt · .env · .strings.json
├── .setup · .install_requirements.py · .admin_wipe_and_create.py · .demo_seed.py
├── run.py · run_server.py · render-build.sh
├── config/        # settings · urls · asgi/wsgi
├── core/          # branding · school details · academic spine · roles · scoping · db router
├── apps/          # the domain apps (see the app map above)
├── templates/     # all templates, per app
├── static/        # css, js, vendor, images
├── locale/        # translations
├── docs/          # integration & operations guides
└── deploy/        # systemd / launchd / cron units for the web app and scheduler
```

For a fuller tour of every feature and the conventions behind them, read `NEW_FEATURES.md`.

<div align="center">
<sub>© 2026 United Church Schools · <a href="https://www.ucs.org.za">www.ucs.org.za</a> · 44 Frances Street, Yeoville, Johannesburg 2198 · 011 648 4727</sub>
</div>
