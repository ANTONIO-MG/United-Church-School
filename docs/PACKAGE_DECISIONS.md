# Third-party package review

Seven packages were proposed. Four are now in the project, three were rejected
because the platform already had a solution that was better on the criteria that
were asked for — efficiency, scalability, performance, security and how easy the
result is to live with.

| Package | Decision | Why |
|---|---|---|
| `django-axes` | **Adopted** | Real gap. See below. |
| `django-import-export` | **Adopted** | No import path existed at all. |
| `sentry-sdk` | **Adopted** (dormant) | No aggregated error reporting existed. |
| `django-otp` | **Rejected** → `allauth.mfa` | allauth already owns the login flow. |
| `channels` | **Adopted** (was rejected) | Real-time *push* (instant chat + notification/message sounds) needs a socket; polling stays as fallback. See [WEBSOCKETS.md](WEBSOCKETS.md). |
| `django-fsm` | **Rejected** → model-level transitions | Package is archived; 30 lines does the job. |
| `django-autocomplete-light` | **Rejected** | Django's built-in `autocomplete_fields` is already in use. |

---

## Adopted

### django-axes — brute-force protection

**What was already there.** allauth's `ratelimit` is called on the login, signup
and password-reset views (`apps/myhub/views.py`), throttling by IP and by the
`login_failed` key.

**Why that wasn't enough.** It throttles a *request rate*; it does not lock an
account, it keeps no record, and there is nothing an administrator can inspect
or clear afterwards. If somebody spends a night grinding an account, nobody ever
finds out.

**What axes adds.** Persistent `AccessAttempt` / `AccessLog` / `AccessFailureLog`
rows visible in the admin, per-account lockout with a cool-off, and a reset an
administrator can perform. The two layers stack: allauth blunts the request
rate, axes stops and records the campaign.

**Configuration** (`config/settings.py`):

- `AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]` — locks the
  *combination*. Locking on username alone lets an attacker deny a real user
  access to their own account; locking on IP alone takes out a whole office
  behind one NAT address because of one bad actor.
- `AXES_FAILURE_LIMIT = 6`, `AXES_COOLOFF_TIME = 30 min` (both env-tunable).
- `AXES_SENSITIVE_PARAMETERS` covers `password`, `password1`, `password2` and
  `token`, so attempted credentials are never written to the attempt log.
- `AxesStandaloneBackend` is **first** in `AUTHENTICATION_BACKENDS` and
  `AxesMiddleware` is **last** in `MIDDLEWARE` — both orderings are required.
- Locked-out users get `templates/account/lockout.html`, which deliberately
  reveals nothing about whether the account exists.

Behind a proxy, set `AXES_PROXY_COUNT` to the number of trusted hops, otherwise
every request looks like it comes from the load balancer.

### django-import-export — Excel/CSV in and out

**What was already there.** `apps/analytics/services.export_rows_xlsx` writes an
xlsx for a handful of analytics reports. Nothing could *import*, and grades and
certificates had no export at all.

**What was built on it.**

- `apps/accounts/resources.PersonResource` — import and export people, keyed on
  **e-mail** (this platform's real identity; nobody chooses a username). A row
  for a new address creates the `User`, whose post-save signal creates the
  `Person`; an existing address updates the profile. **Passwords are never
  imported** — a new account is created with an unusable password and the person
  sets their own through the normal reset e-mail.
- `apps/reports/resources.GradeResource` — **export only**, on purpose. Grades
  are computed from assessments, tasks and study time by
  `apps.reports.services`; letting a spreadsheet write them back would silently
  overwrite that calculation. The JSON component breakdown is flattened to one
  column each so the export is sortable and chartable.
- `apps/reports/resources.CertificateResource` — issued certificates with their
  verification UUIDs.

Reachable from the Django admin changelists for Person, Grade and Certificate.

### sentry-sdk — error reporting

`LOGGING` records what happened on *one* server. Sentry aggregates unhandled
exceptions across all of them with a stack trace, the triggering request and a
recurrence count.

It is **completely inert without `SENTRY_DSN`**, so development is unchanged.
`send_default_pii` defaults to **False**: no request bodies, no cookies and no
logged-in identity leave the platform unless someone explicitly opts in.
`traces_sample_rate` defaults to 0.05 — full tracing on a busy LMS is expensive
and rarely more informative than a representative sample.

---

## Rejected, with what was done instead

### django-otp → `allauth.mfa`

The requirement (multi-factor authentication) is real and is now **implemented** —
just not with this package.

django-allauth 65 ships its own `allauth.mfa` app. Because allauth already owns
login, signup, social login, e-mail verification and password reset here,
`allauth.mfa` slots into all of them at once. django-otp would have meant a
second, parallel login pipeline to keep in step with the first — two places to
get the social-login and reauthentication edge cases right instead of one, which
is exactly how MFA bypasses happen.

Enabled: TOTP (any authenticator app) plus one-time recovery codes, at
`/accounts/2fa/`. `ACCOUNT_REAUTHENTICATION_REQUIRED` makes the user re-enter
their password before adding or removing a factor, so a hijacked session cannot
quietly swap the second factor for the attacker's own.

Set `MFA_REQUIRED_FOR_STAFF=true` to make it compulsory for accounts that can
change other people's data — staff, superusers and anyone whose profile type is
admin, staff or educator. `apps.accounts.middleware.MfaRequiredMiddleware`
enforces it; learners and parents are never affected. It is **off by default**.

Extras installed: `qrcode` (enrolment QR) and `fido2` (imported unconditionally
by `allauth.mfa`, even with WebAuthn switched off).

### channels — WebSockets — **adopted** (this section supersedes the original rejection)

Originally rejected because a polling system already worked on plain WSGI. It was
picked up once real-time *push* became a first-class requirement — instant chat
delivery and, above all, **notification/message sounds that play the moment
something arrives** rather than up to 20 seconds later. A sound is only useful if
it is immediate; polling cannot give you that without hammering the server.

What was added (full detail in [WEBSOCKETS.md](WEBSOCKETS.md)):

- `daphne` + `channels` in `INSTALLED_APPS`, `ASGI_APPLICATION`, and a
  `CHANNEL_LAYERS` that is **in-memory for a single dev process** and **Redis when
  `USE_REDIS=true`** — no new infra is forced on anyone who does not turn it on.
- `config/asgi.py` protocol router; `apps/communication/{routing,consumers,realtime}.py`.
- Producers in `notify()` and `MessageViewSet.perform_create`.
- Clients in `static/js/chrome.js` (alerts) and `_chat_script.html` (chat).

Crucially the original concern — "don't destabilise a working feature" — is
respected: **polling stays as the fallback**. With `WEBSOCKETS_ENABLED=false` or
no ASGI server, the sockets simply aren't used and the app behaves exactly as
before. The change is additive, not a rip-and-replace.

### django-fsm — assessment states

**The requirement was right.** `authoring.create` took the new assessment's
status straight from `request.POST.get('status')` with no validation, so an
assessment could go from Draft to Open — visible to learners — in one hop, with
no questions in it.

**The package was wrong.** `django-fsm` is archived and unmaintained; adopting it
means adopting a fork (`django-fsm-2`) as a permanent dependency.

**What was done instead** (`apps/assessments/models.py`): a `review` state was
added, alongside `STATUS_TRANSITIONS` (a dict of which state may follow which)
and `transition_to()`, which refuses anything the map doesn't allow *and*
refuses to open a paper with no questions in it. `available_transitions()` feeds
the builder's "Move to…" menu, so the UI only ever offers moves the server will
accept. Roughly thirty lines, no dependency, no new vocabulary.

The lifecycle: `Draft → Review → Scheduled/Open → Closed → Archived`, with
Review able to send work back to Draft and Archived able to reopen as Draft.

### django-autocomplete-light — autocomplete fields

Already solved, by Django itself. `autocomplete_fields` is used across
`apps/assessments/admin.py`, `apps/accounts/admin.py`, `apps/learning/admin.py`,
`apps/reports/admin.py` and `apps/tasks/admin.py` — Select2-backed, paginated,
permission-checked, and maintained as part of Django.

django-autocomplete-light matters when you need autocomplete on **non-admin**
forms. The public-facing forms here are short and mostly pick from small,
fixed lists, so it would add a dependency and a static-asset pipeline for
nothing. If a public form ever needs to search thousands of rows, revisit it.
