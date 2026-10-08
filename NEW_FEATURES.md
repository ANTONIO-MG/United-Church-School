# United Church School LMS — Complete Feature Guide & Developer Orientation

> **What is this project?**
> The United Church School (UCS) learning platform (branded *"My Learning Hub"*) is a Django
> platform that runs the whole school — Grade 1 to Grade 12, CAPS subjects, learners,
> parents, teachers and the school office — from one place. It combines an
> **LMS** (courses, lessons, assessments, grading, analytics), a **community/social layer**
> (profiles, messaging, discussions, events), **e-commerce** (shop, cart, invoicing,
> PayFast payments), **operations** (tasks, meetings, attendance) and a **dual-layer AI
> assistant**. Everything renders through one shared, role-aware Bootstrap 5 "Social" theme.

> **How the school maps onto the data model.** One `Institution` — the school (code `UCS`) →
> `Programme` = a grade (`GR01` … `GR12`) → `ProgrammeModule` = a CAPS subject offered in that
> grade → `Cohort` = a class / year group. The code keeps the generic names (institution,
> programme, module, cohort); everything the user sees says school, grade, subject and class.

This document is the **single map of everything the project can do**. If you're new, read
"How the project is wired" first — it explains the conventions every feature follows — then
skim the feature sections. URLs and the role model are at the bottom.

---

## Registration, enrollment, POPIA & invites (2026 additions)

**Sign-up → activation → onboarding.** Sign-up is e-mail-only (`/myhub/page-register/`) with
a reCAPTCHA v2 checkbox (shown/enforced only when `RECAPTCHA_SITE_KEY`/`SECRET_KEY` are set).
E-mail verification is **mandatory** (`ACCOUNT_EMAIL_VERIFICATION`); the account can't sign in
until the activation link is clicked. After first login, `OnboardingMiddleware` forces
registration.

**3-step student registration wizard** (`apps/accounts` · `accounts:register` → `-course` →
`-review`): Step 1 personal detail (grouped `Person*` side-tables + OpenStreetMap/Photon
address autocomplete + POPIA consent), Step 2 course picker with rich detail + paid add-ons
(`myhub.CourseAddon`) or products, Step 3 review → checkout. Progress is saved per step.

**Grouped profile models** (`apps/accounts/models.py`): `PersonContact`, `PersonEducation`,
`PersonStudyProfile`, `PersonFunding`, `PersonTech`, `PersonConsent` — OneToOne to `Person`,
created lazily. `Course` gained rich fields (outcomes, sessions, certificate, pass mark, …).

**Payment & enrollment.** Registration creates a `finance.Invoice` and routes through the
existing PayFast checkout (free enrolments confirm immediately). On settlement the
`finance.invoice_paid` signal → `accounts.services.fulfil_paid_registration`: enrols the
student (course + subjects + chat groups) when `ENROLLMENT_MODE=auto`, posts a chat welcome,
and e-mails a summary **with a PDF invoice** (`xhtml2pdf`). `ENROLLMENT_MODE=manual` records
payment and shows an "Awaiting enrolment" panel on the members page for one-click admin enrol.

**POPIA (`Settings → Privacy & consent`).** Mandatory + optional consents recorded on
`PersonConsent` with audit (date/version/IP/device); **data export** (PDF or JSON), account
deletion, and a site-wide **cookie-consent banner**. A full POPIA privacy policy lives at
`/social/privacy-and-terms/` (public).

**Invite-based parent & educator registration.** A single-use `accounts.Invitation` carries
the role + target so the invitee never picks a type. Learners name their parent/guardian/
sponsor e-mails during registration → each gets an invite; admins invite educators via
*Members → Invite educator* (email + course). The link routes: sign-up → verify → a **single**
role registration page (parents confirm the student; educators confirm the course) → linked +
summary e-mail. The link expires on completion.

**Branded e-mails** embed their logo/header/footer/social images inline (CID) so they render
in any inbox regardless of `SITE_URL`.

Relevant env: `ENROLLMENT_MODE=auto|manual`, `RECAPTCHA_SITE_KEY`/`RECAPTCHA_SECRET_KEY`,
`ACCOUNT_EMAIL_VERIFICATION=mandatory`. New dependency: `xhtml2pdf` (in `requirements.txt`).

---

## How the project is wired (read this first)

| Concept | Where | What to know |
|--------|-------|--------------|
| **Apps** | `apps/*` | Each domain is its own Django app (see the map below). Business logic lives in `services.py`, not views. |
| **Templates** | `templates/<app>/` | **All** templates live in the root `templates/` folder, organised per app (`templates/accounts/`, `templates/communication/`, …). There are **no** `apps/*/templates/` folders — edit templates here. |
| **Shared layout** | `templates/myhub/elements/layouts/admin.html` | The one canonical page chrome (navbar + sidebar + footer + `{% block content %}`). **Every signed-in page extends only the body.** Public pages extend `templates/base.html`. |
| **Branding & copy** | `.strings.json` (project root) + `core/branding.py` | Logo, org name, contacts, socials, welcome text and dynamic-widget toggles all come from one JSON file. Templates read `brand` / `org` / `dynamic` / `site`; use the `t()` helper / `org_brand` tag for strings. **Never hard-code user-facing text.** |
| **Roles** | `core/roles.py` → `role_flags(request)` | Five roles — `student`, `parent`, `educator`, `staff`, `admin` (no `regular`/`guest`). Flags drive UI + data scoping: `is_admin_staff`, `is_educator`, `is_student`, `is_parent`, plus **permission** flags `can_manage` (full CRUD, admin/staff), `can_teach` (educators, teach-only), `can_pay`. Exposed to every template via the `user_roles` context processor. |
| **Auth** | `django-allauth` | E-mail-only login (username = e-mail), e-mail verification, password reset, "Continue with Google". |
| **Access gates** | `apps/accounts/middleware.py` | `LoginRequiredMiddleware` (site-wide login) + `OnboardingMiddleware` (forces registration → profile completion before the dashboard) + `ManagementAccessMiddleware` (redirects non-admin/staff away from CRUD/management URLs). The first two keep `_EXEMPT_PREFIXES` lists. |
| **Dashboard data** | context processors | Sidebar/dashboard widgets are fed by per-app context processors (`account_stats`, `comm_stats`, `shop_stats`, `finance_stats`, `task_stats`, `get_dashboard_data`) — all registered in `config/settings.py`. |
| **Migrations** | `python manage.py makemigrations` | Develop in a virtualenv (`python -m venv .venv`, `.gitignored`); the working freeze is `installed_packages.txt` (Django 6.0.6). Generate migrations normally and run `python manage.py migrate` after pulling. |
| **E-mail** | `apps/communication/emails.py` + `communication/email/*.html` | **One** branded e-mail library. Call typed senders (`send_invoice_email`, `send_purchase_email`, `send_password_changed`, …) or `send_branded_email(subject, to, template, ctx)`. Don't create per-app e-mail templates. |
| **AI** | `apps/ai_assistant` | Two layers (local CrewAI + admin Claude) — both optional and degrade gracefully when not configured. |

### App map

```
apps/accounts       identity, profiles, Subjects, course enrolment, onboarding, registration, parent links, audit log
apps/myhub          dashboard, organisation models (Course = academic spine · students/staff…), calendar & events, landing
apps/communication  messaging/chat (+ student connection gate), in-system mail, meetings (Jitsi), notifications,
                    announcements, discussions, attendance, collaboration workspaces, e-mail library
apps/ai_assistant   local CrewAI assistant + media pipeline + activity digest; AI Studio (report cards,
                    assignments, parent msgs, minutes, ask-the-data) + AI Secretary; advanced admin Claude chat
apps/shop           products & services store (courses are buyable), cart, ratings & reviews
apps/finance        invoices, invoice items, cart→invoice, PayFast checkout, payments, receipts, history
apps/tasks          assignable tasks (per user/subject/course/department/all) with progress; can deliver SCORM/LTI
apps/learning       block-based lesson creator (LessonBlock) + viewer, modules/lessons, study timers,
                    authored courses (module segments) + player + SCORM export
apps/assessments    quizzes/tests/exams, questions, attempts, take-engine + auto-marking, weighting
apps/scorm          SCORM 1.2/2004 import (scorm-again runtime) + native-lesson EXPORT → gradebook/tasks
apps/lti            LTI 1.3 + Advantage — Tool (deep-link → content) + Platform (AGS → grade + task)
apps/lrs            self-hosted xAPI/cmi5 LRS (Statement/State API + cmi5 launcher + viewer + gradebook ingest)
apps/reports        weighted grades, letter scales, report cards, certificates
apps/analytics      academic intelligence & risk monitoring (admin/staff/educator)
```

---

## 1 · Accounts, identity & onboarding

- **People & roles** — `Person` profile per user (name, contact, **address**, gender, DOB,
  bio, picture, emergency contact, `user_type`). Five roles: **student, parent, educator, staff,
  admin** (new sign-ups default to `student`; the old `regular`/`guest` types were removed).
  Permissions: admin/staff = full CRUD; educators = teach-only; parents = view + payment; students
  = view own + pay. Enforced in the UI *and* by `ManagementAccessMiddleware`.
- **Courses & subjects** — the platform is course-centric: a **`myhub.Course` has many
  `accounts.Subject`**. A **student belongs to ONE course** (`Person.course`) and is
  **auto-enrolled in every subject** of it; **educators teach subjects** (assigned by staff/admin).
  `accounts.services.enrol_person(person, course, subject_ids=None)` does the enrolment;
  staff/admin fine-tune membership on `/community/members/<pk>/enrol/`.
- **Registration** — `/community/register/` is a single-page signup capturing profile + role,
  and — **for students** — the ONE course to enrol in (raising an enrolment invoice; picking a
  course auto-joins all its subjects). First sign-in is forced through it by the onboarding
  middleware. On completing as a student it e-mails a **registration summary** and generates a
  **parent-invite link**. Educators/parents just register (an admin later assigns an educator's
  subjects; a parent picks their child).
- **Parent/guardian invites** — `ParentLink` ties parents to a student, **max 2 per student**.
  `/community/parents/<token>/` lets an invited parent self-register and link to the child.
- **Audit log** — `ActivityLog` records actions; surfaced on profiles and the dashboard.
- **Profile page** — `/community/my-profile/` (and `/profile/<id>/`): social-style header
  (cover, avatar, role, stats) with **About / Activity / Posts** tabs (enrolment, recent
  `ActivityLog`, authored discussions).
- **Members directory** — `/community/members/` with a **grid ⟷ list toggle** (grid default,
  remembered per browser); each member links to a full **profile page** (`accounts:member-profile`)
  modelled on the social "about" layout, where owner-only buttons (Edit profile) show only to the
  signed-in user and are gated by their **privacy** settings.
- **Functional settings** — `/community/settings/` is a tabbed hub (account details · privacy &
  preferences · notifications · security/password · close account) backed by a **`UserSettings`**
  model (`profile_visibility`, `show_email`, `show_activity`, `allow_messages`, `theme`, `language`,
  `email_digest`). Privacy actually gates the member profile page; password change keeps the session.
- **Close account (30-day grace)** — `accounts:close-account` verifies the user (re-enter
  password / e-mail / `CLOSE`), then **soft-closes** (deactivates + stamps `purge_at = now + 30d`)
  and signs out. The `purge_closed_accounts` management command later **archives a JSON snapshot**
  (to an `AccountArchive` row + `backups/archived_accounts/…json`) and deletes the live record.
- **Auth** — allauth e-mail login, verification, password reset, Google OAuth.

## 2 · MyHub — dashboard, organisation & calendar

- **Dashboard** (`/myhub/`) — social-feed style, **role-aware**. It now opens with a
  **"Share your thoughts" composer** and the **unified activity feed** (`build_feed()` — posts,
  announcements, notifications, messages, tasks, events & reminders merged by time), plus a right
  rail of **your tasks / people you may know / quick links** and an AI-insights highlight for
  educators/admins. `/social/` renders the same feed inside the shared chrome (no more separate
  shrinking layout). The old stories carousel was removed.
- **Organisation models** — students, courses, professors, staff, departments, library items,
  holidays, each with CRUD + counts feeding the dashboard.
- **Calendar** (`/myhub/event-management/`) — FullCalendar rendering of an **aggregated feed**
  (`events_feed`): institution events, personal reminders, holidays, task deadlines, lesson
  publish dates, assessment close dates and meetings — colour-coded and scoped to the user.
  Users add personal reminders via `/myhub/add-reminder/`.
- **Events** (`/myhub/events/`) — the same calendar sources as an Edumin/"events-2"-style card
  list (Upcoming + Recently); `/myhub/events/<id>/` is an event detail page.
- **Landing page** — public marketing page for signed-out visitors.

## 3 · Communication — messaging, mail, meetings, notifications

- **Messaging / chat** (`/communication/chat/`) — social-messaging UI (conversation rail with
  avatars + search + person picker; thread with bubbles, attachments, @mentions, edit-your-own).
  Now with **voice & video-call buttons** on the conversation header, a **typing indicator**,
  **unread blue rings + green "new" badges** on conversations, and **sounds** for new messages /
  incoming live meetings (client-side over the `chat-groups` `last_message` + `meetings`
  `is_live_now` APIs). Conversation types: **course** (group), **subject**, **direct (1:1)**,
  **custom** groups and a platform-wide **General** channel. Backed by the DRF API at
  `/api/communication/`.
- **Connection-gated student DMs** — two **students** can only 1:1 direct-message once one sends
  a **connection request** and the other **approves** it (`ConnectionRequest`; states
  none → sent → incoming → connected). Enforced **server-side** (`MessageViewSet.perform_create`
  rejects a gated send) *and* in the UI: the chat compose box becomes a Request / Approve / Pending
  banner, and the member profile shows a **Connect / Pending / Approve / Connected** button. A
  request notifies the recipient; an accept notifies the requester. **Course/subject/custom group
  chats stay open** to all members, and any chat involving a staff/admin/educator/parent is never
  gated. Helpers: `services.students_need_connection`, `are_connected`, `can_direct_message`,
  `direct_gate_state`, `request_connection`, `respond_connection`; routes under
  `/communication/connect/…`.
- **Unified feed** — a new `Feed` model (author, body, image/video/file media, visibility
  public/groups/staff) + `feed.build_feed(user)` aggregator that merges Feed posts, announcements,
  the user's notifications, direct & group messages, tasks and calendar events/reminders by
  timestamp; posted from the composer (`communication:feed-create`) and rendered on the dashboard
  and `/social/`.
- **In-system e-mail** (`/communication/mail/`) — an inbox/compose/read **mailbox for
  admin·staff·educators** (folders: inbox/sent/starred/trash, search). Sending stores the
  message *and* delivers a real branded e-mail per recipient, reply-to the sender's address.
- **Meetings** — Jitsi-backed video/audio rooms (`MeetingRoom`), host/invite, join links.
- **Discussions** — threaded forum (`Discussion` + replies), with chat moderation.
- **Notifications** — bell badge + `/communication/notifications/`; each opens a full
  **blog-style detail page** (`communication:notification-detail`) and is **marked read on open**
  (mail and chat messages do the same). Honours per-user `NotificationPreference` (channel/category
  switches, digest, quiet hours, reminder lead). `scan_deadline_reminders()` raises "due soon"
  alerts for tasks/assessments.
- **Announcements** — bulk branded announcements to roles/courses.
- **Attendance** — `ClassSession` + `Attendance`; auto check-in when a student joins a live
  class call, self check-in, and educator roll-marking (`/communication/attendance/`).
- **Collaboration workspaces** — `/communication/workspaces/`: shared files (with re-upload
  **versioning**) and pinnable project notes, scoped to a group/subject's members.
- **Real-time push (WebSockets / Django Channels)** — sockets deliver events the instant
  they happen: a per-user `ws/alerts/` chimes the navbar bell + shows its dot the moment a
  notification or an addressed message arrives (no poll delay), and a per-conversation
  `ws/chat/<id>/` refreshes any open messenger immediately on a new message; and a per-lesson
  `ws/lesson/<id>/` shows a live **"who's here now"** roster in the lesson rail plus
  **hand-raising** (a raise/lower toggle everyone sees, with a "N hands up" list) — peer-announced,
  access-gated by `_can_view_lesson`. **Polling is kept as an automatic fallback**, so with
  `WEBSOCKETS_ENABLED=false` or no ASGI server everything still works. `daphne` gives `runserver`
  sockets in dev; production runs `config.asgi` with a **Redis** channel layer when
  `USE_REDIS=true` (in-memory otherwise). Files: `config/asgi.py`, `apps/communication/{routing,
  consumers,realtime}.py`; producers in `notify()` and `MessageViewSet`; clients in `chrome.js`,
  `_chat_script.html` and the lesson player. Full guide: **`docs/WEBSOCKETS.md`**.

## 4 · AI assistant (dual-layer, both optional)

- **Layer 1 — local, everyone.** A CrewAI floating widget answers page questions; a **media
  pipeline** turns dropped video/audio/PDF/text into a transcript → summary → proposed actions
  that wait in a **To-Do/Reminders approval inbox** (`/assistant/`) until approved into real
  Tasks/Events/Meetings/Emails/Invoices. An **activity digest** (`scan_activity`) summarises
  recent activity into personalised inbox items. 100% local (Ollama + faster-whisper).
- **Layer 2 — advanced admin Claude (admin/staff only).** A full-screen claude.ai-style chat
  (`/assistant/chat/`) backed by the **Anthropic SDK** (`admin_ai.py`), grounded in live
  analytics, with streaming + **per-message token accounting** (`AdminAIThread`/`AdminAIMessage`).
  Off until `ANTHROPIC_API_KEY` + `ADMIN_AI_ENABLED` are set.
- **AI Studio — the local Teaching Assistant (educators/admins).** A CrewAI + Ollama agent set
  that **reads and queries the database** and drafts documents at `/assistant/studio/`:
  - **Ask the data** (`/assistant/studio/ask/`) — natural-language questions ("who missed >3 Maths
    classes?") routed to a **registry of safe ORM queries** (no arbitrary SQL) and narrated.
  - **Report cards**, **parent messages**, **assignment generator** (creates a *real draft
    assessment* + rubric/memo, opens in Build Assessments) and **meeting minutes** (summary /
    decisions / attendance / action items → inbox).
  - **AI Secretary** (`/assistant/insights/`, `run_secretary` command/Celery task) — a proactive
    DB scan that surfaces `AiInsight`s: overdue assessments, missing attendance, at-risk/failing
    learners, overdue tasks and attendance drops. Acknowledge / dismiss / act.
  - Every output is an `AiReport` (Markdown) rendered in-theme with finalize/download. **100%
    local** — uses the same `AI_ASSISTANT_ENABLED` + `AI_LLM_MODEL` (Ollama) settings; when the
    model is offline each feature falls back to a deterministic template built from real data.

## 5 · Shop & e-commerce

- **Storefront** (`/shop/`) — products **and services** shown as Edumin course-cards with
  educator, price, level, duration, **ratings & reviews** (`ProductReview`). MyHub **courses are
  buyable** items (catalog sync in `shop/services.py`).
- **Cart** (`/shop/cart/`) — the `Order` model doubles as the cart via a `checked_out` flag;
  add / update / remove items.

## 6 · Finance — invoicing & payments

- **Invoices** — `Invoice` + `InvoiceItem` (line items auto-populated from a product/service/
  course or built from scratch), public `public_id` + pay URL. Admins/staff create and send
  invoices (emailed **pay-link**) to a user or a whole **course**; students & parents buy & view their own.
- **Cart → checkout → pay** — `create_invoice_from_order` turns a cart into an invoice;
  `/finance/checkout/` → `/finance/pay/` runs **PayFast** (signed redirect + ITN webhook,
  sandbox by default). `settle_payment` is idempotent and produces a **receipt** and settles the
  order. Filtered **payment history** (paid/upcoming/overdue).
- **E-mails** — invoice, receipt/payment-made and purchase confirmations via the central library.

## 7 · Tasks

Assignable tasks scoped per user / group / subject / course, with per-assignee **progress**
and status; feeds the dashboard "My tasks" widget and deadline reminders.

## 8 · Learning Hub (LMS core)

- **Learning** — modules and **lessons** and study-session timers; `/learning/`.
- **Lesson creator** (`apps/learning/authoring.py`) — a **block-based lesson editor** at
  `/learning/lessons/manage/` → **New lesson** → `/learning/lessons/<id>/edit/`. A lesson is an
  ordered list of **`LessonBlock`s** (typed `data` JSON): **heading · rich text · image · video ·
  audio** (upload *or* YouTube/Vimeo/URL, played via Plyr) **· embedded trackable page** (iframe +
  a viewing heartbeat → xAPI) **· file · reference · callout · divider · quiz** (reuses the
  `assessments` engine) **· live session** (a Jitsi `MeetingRoom` embedded in the lesson). Blocks
  **drag-to-reorder** (vendored `static/js/sortable-lite.js`), **autosave** over `JsonResponse`,
  media uploads with a progress bar. Set **author + bio + references**, then **publish** to a
  subject / class / **individuals**. Learners read it at `/learning/lessons/<id>/view/` (progress
  bar, media players, embeds, lazy-join meetings, "Mark complete") — emitting xAPI throughout.
  **Export** the lesson (with its media) as a real **SCORM 1.2 or 2004** package, or *"publish as
  playable SCORM"* to round-trip it into the in-hub player.
- **Authored courses** — a **Module becomes a playable course** built from ordered **segments**
  (`ModuleItem`: heading · lesson · assessment · SCORM). Educators assemble them in the
  **builder** (`/learning/courses/<m>/build/`, drag-to-reorder, required + gating); learners walk
  them in the **player** (`/learning/courses/<m>/play/`) which tracks progress, rolls completion
  into grades + a **module certificate**, and can **export the module as a SCORM 1.2 package**
  (`/learning/courses/<m>/export/`).
- **Assessments** — quizzes/tests/exams + a full **take-engine**: sections → questions, resume,
  timer, attempt limits; `/assessments/<id>/take/` → `/…/result/`. Per-assessment **`component`**
  decouples the report-card bucket from the kind (so SCORM/LTI count too), plus **`weight`** and
  **`is_extra_credit`**.
- **Per-question builder + dynamic marking** — a no-admin **builder** (`/assessments/manage/`,
  `/…/build/`) where each question is created with a **marking mode chosen at creation**: *auto*
  (define the key — correct choices / accepted answers — and it's machine-marked) or *manual*
  (write a **rubric** and grade it yourself). Not flagged manual → the builder auto-marks it.
  Objective answers score on submit; manual ones land in a **marking queue**
  (`/assessments/marking/`) where the educator is prompted with each rubric + response, awards
  marks + feedback, and the attempt is re-graded. `total_marks` auto-syncs to the questions.
- **SCORM** (`apps.scorm` + `apps/scorm/export.py`) — **import**: upload a SCORM 1.2/2004 `.zip`;
  it unpacks, parses the manifest and plays in-hub via **scorm-again** (now seeded with the
  learner's identity, full-CMI resume, `entry` and mastery). Completion/score commits back and
  folds into the bound assessment (report card), any delivering task, and the lesson's study
  session. **export**: turn a native lesson (with its media) into a standards-compliant SCORM 1.2
  or 2004 package that reports completion/score/time — and re-import it. `/scorm/`.
- **LTI 1.3** (`apps.lti`) — the hub as both **Tool** (an LMS launches into our content; **deep
  links now open the exact bound lesson/quiz** — the `custom.lesson_id`/`assessment_id` loop is
  closed — grades sync out via AGS) and **Platform** (we launch an external tool; AGS grades come
  back into **both** the bound assessment's grade **and** the delivering task's `TaskAssignment`).
  OIDC + RS256 JWT + JWKS; `/lti/` (config), `/lti/login/`, `/lti/launch/`, `/lti/platform/…`.
- **xAPI / cmi5 LRS** (`apps.lrs`) — a **self-hosted Learning Record Store** in Postgres. Native
  lessons, **per-question quiz interactions** (`answered` cmi.interaction statements), SCORM and
  assessments emit xAPI. Statement/State API at `/xapi/`, cmi5 launch + fetch at `/lrs/cmi5/…`
  (with an **AU launcher** surfaced on the lesson dashboard that can bind an assessment), and a
  staff **learning-records feed** at `/lrs/`. **Imported completion → gradebook** (`apps/lrs/ingest.py`):
  a completion/pass statement from a cmi5 AU (or any external xAPI targeting a bound activity)
  folds into the local gradebook via `record_external_result` — external content grades like
  native content. Internal emissions are never re-graded (no loop).
- **Reports & grading** — `compute_grade` does a **weighted mean within each component** (bucketed
  by each assessment's `component`), adds capped **extra-credit bonus**, renormalises over
  available components, and maps the final % to a **letter** via the subject's custom
  `grade_scale`. Produces **report cards** and **certificates**; `/reports/` (incl. the
  per-student **progress dashboard** at `/reports/progress/` with Chart.js).
- **Analytics** — academic intelligence and **risk monitoring** for admins/staff/educators;
  `/analytics/`. Also grounds the advanced admin AI.

## 9 · Cross-cutting UX

- **Shared app chrome** (`static/css/chrome.css` + `static/js/chrome.js`, loaded by both
  layouts) — the single place that owns global navbar/sidebar behaviour:
  - **Navbar** — every item (logo, org title, search, collapse button, right menus) sits on a
    consistent baseline with even breathing room; main menus get themed icons + rotating carets.
  - **Sidebar** — sticky and independently scrollable; **remembers its collapsed/minimised state
    *and* scroll position** across pages (localStorage), and **reveals on hover** of the far-left
    edge when collapsed.
  - **Loaders** — extends `_loader.html` with `window.appLoader.progress(pct)` for
    uploads/downloads, `.is-loading` button spinners, skeleton/fade utilities, and auto-shows
    around `fetch()`.
  - **Sounds** — `window.appSound.message()/notify()/call()/stopCall()` (WebAudio, no assets)
    for new messages / notifications / incoming calls.
- **Unified activity feed** — a "Share your thoughts" composer (`partials/_composer.html`) +
  `partials/_feed.html` render `communication.feed.build_feed()` on both `/myhub/` and `/social/`
  (see §2/§3). The old stories carousel was removed.
- **Form focus styling** — the shared CRUD form renderer (`myhub/elements/_form.html`) tags forms
  `.app-form`; chrome.css turns any card wrapping one into a compact, centred, bordered "focus"
  card with a soft blurred backdrop. Django ModelForm edits prepopulate from the instance.
- **Global loading indicator** — `templates/partials/_loader.html` (top progress bar + spinner)
  in both layouts; auto-shows on navigation/form submit; `window.appLoader.show()/.hide()` for AJAX.
- **"Social" Bootstrap 5 theme**, dark/light, Inter font; **All-Content** component reference at
  `/myhub/all-content/`.

## 10 · Run on your network + multiple sign-ins

- **`python run_server.py`** binds the dev server to `0.0.0.0` and prints the shareable **LAN
  URL(s)** so anyone on the same Wi-Fi opens `http://<computer-ip>:8000`. `ALLOWED_HOSTS` defaults
  to `*` and `config/settings.py` **auto-detects the machine's LAN IP and trusts it as a CSRF
  origin** (plus anything in the `CSRF_TRUSTED_ORIGINS` / `LAN_PORTS` env vars) so login and all
  form POSTs work from other devices.
- **Concurrent users** — every device/browser holds its own session; unlimited users can be signed
  in at once and the app never force-logs-out other sessions. For **two accounts on one computer**,
  use a second browser or an Incognito/Private window (separate cookie jars).

---

## URL quick reference

| URL | What |
|-----|------|
| `/` | redirect to dashboard (or landing if signed out) |
| `/myhub/` · `/social/` · `/myhub/events/` · `/myhub/event-management/` | dashboard (feed) · social feed · events list · calendar |
| `/community/register/` · `/community/parents/<token>/` · `/community/my-profile/` | wizard · parent invite · profile |
| `/community/members/` · `/community/members/<id>/` · `/community/settings/` · `/community/settings/close/` | members (grid/list) · member profile · settings · close account |
| `/communication/chat/` · `/communication/mail/` · `/communication/workspaces/` · `/communication/attendance/` · `/communication/notifications/` | messaging · mail · workspaces · attendance · alerts |
| `/shop/` · `/shop/cart/` | store · cart |
| `/finance/` · `/finance/checkout/` · `/finance/pay/` | invoices · checkout · PayFast |
| `/tasks/` · `/learning/` · `/learning/courses/` · `/assessments/` · `/reports/` · `/reports/progress/` · `/analytics/` | tasks · LMS · courses |
| `/learning/courses/<m>/build/` · `/…/play/` · `/…/export/` | course builder · player · SCORM export |
| `/assessments/<id>/take/` · `/assessments/attempt/<uuid>/result/` | take a quiz/test · result & review |
| `/scorm/` · `/scorm/<pkg>/launch/` | SCORM library/upload · play a package |
| `/lti/` · `/lti/login/` · `/lti/launch/` · `/lti/jwks/` · `/lti/platform/…` | LTI config · Tool launch · Platform endpoints |
| `/lrs/` · `/xapi/statements` · `/xapi/activities/state` · `/lrs/cmi5/…` | xAPI feed · Statement/State API · cmi5 |
| `/assistant/` · `/assistant/chat/` | AI inbox · advanced Claude chat (admin/staff) |
| `/assistant/studio/` · `/assistant/insights/` · `/assistant/reports/<uuid>/` | AI Studio · AI Secretary insights · generated document |
| `/admin/` · `/api/…` | Django admin · REST (`auth`, `token`, `accounts`, `myhub`, `communication`, `ai`) |

## Roles at a glance

| Role | Sees / can do |
|------|---------------|
| **Student** | own profile, their **one course** + all its subjects, tasks, assessments, progress, attendance, messaging (student↔student DMs need an accepted connection), shop & own invoices; can invite up to 2 parents |
| **Parent/Guardian** | linked child's relevant info; **view + payment only** (buy & view own invoices) |
| **Educator** | **teach-only** — teaching subjects, roll-marking, lessons/assessments, in-system mail, workspaces (no CRUD of courses/subjects/people) |
| **Admin/Staff** | **full CRUD** institution-wide, invoicing to users/courses, subject-membership editing, announcements, analytics, and the **advanced Claude** layer |

## Configuration & dependencies

- **`.env`** — `SECRET_KEY`, DB (`POSTGRES_*` primary, `MYSQL_*` optional), `EMAIL_*` (SMTP),
  `GOOGLE_OAUTH_*`, `JITSI_BASE_URL`, AI layer 1 (`AI_ASSISTANT_ENABLED`, `AI_LLM_*`,
  `WHISPER_MODEL`), advanced AI (`ANTHROPIC_API_KEY`, `ADMIN_AI_ENABLED`, `ADMIN_AI_MODEL`),
  **PayFast** (`PAYFAST_SANDBOX`, `PAYFAST_MERCHANT_ID`, …), and the **Learning-Hub
  integrations**: `SESSION_COOKIE_SAMESITE`/`SESSION_COOKIE_SECURE` (LTI iframe launches),
  `SCORM_ROOT` / `SCORM_AGAIN_URL` / `SCORM_CONTENT_ORIGIN`, and `LTI_PLATFORM_ISSUER`. The LRS
  needs no env (self-hosted in Postgres). **Keep all secrets in `.env` — never commit them.**
- **Dependencies** — `requirements.txt`; LTI/SCORM/xAPI use `cryptography` + `PyJWT` + `requests`
  + `defusedxml` (all listed) and no other new packages. `scorm-again` and `SortableJS` load from
  a CDN (vendor into `static/` for air-gapped/CSP builds); `anthropic` powers the admin AI; the
  local AI extras (`crewai`, `faster-whisper`, …) are optional. `python .install_requirements.py`
  installs from `requirements.txt`.
- **Reset/seed** — `.admin_wipe_and_create.py` wipes, migrates, creates the superusers **and a
  roster of dev/test users** (educators, students, a parent, staff — all password `Password@99`),
  seeds the org, a **playable course** and the **SCORM/LTI/LRS integration records** (LTI Tool +
  Platform registrations with auto-generated keys, an xAPI credential).
- **Network / LAN** — `ALLOWED_HOSTS` (default `*`), `CSRF_TRUSTED_ORIGINS` (extra trusted form
  origins for a proxy/hostname) and `LAN_PORTS` (ports the auto-detected LAN IP is trusted on,
  default `8000,80,8080`). Start with `python run_server.py` to serve the whole network.
- **After pulling, run** `python manage.py migrate` (recent migrations add `apps.scorm`,
  `apps.lti`, `apps.lrs`, `learning/0002_moduleitem…`, `assessments/0003_assessment_component…`,
  the `tasks` SCORM/LTI delivery FKs, **`communication/0006_feed`** (unified feed) and
  **`accounts` `UserSettings` + `AccountArchive`** (settings & close-account)).
