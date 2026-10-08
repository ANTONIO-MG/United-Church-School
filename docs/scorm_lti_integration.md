# SCORM & LTI 1.3 Integration

This document describes the `apps.scorm` and `apps.lti` apps and the adjustments
made to `assessments`, `tasks` and `reports` so external content plugs into the
existing gradebook. It implements Phases 1–3 of the research plan (self-hosted
SCORM play, LTI 1.3 Tool, LTI 1.3 Platform first pass).

## The one gradebook rule

Everything scored — quizzes, SCORM packages, LTI activities — flows into a single
`assessments.AssessmentAttempt`, whose save recomputes `reports.Grade` via the
existing `reports.signals`. There is **no second gradebook**.

```
SCORM commit ─┐
LTI AGS score ─┼─► assessments.services.record_external_result()
quiz submit  ─┘        └─► AssessmentAttempt (save)
                              └─► reports.signals.recompute_grade_on_attempt → reports.compute_grade
```

## Adjustments to existing apps

### assessments
- New `Assessment.kind` values: `scorm`, `lti`.
- New `Assessment.component` field (`assignments|quizzes|tests|exams`, blank =
  auto from kind). `Assessment.grade_component` returns the effective bucket.
  `reports.compute_grade` now groups assessments by **component** instead of the
  raw kind, so a SCORM/LTI activity (or a re-bucketed quiz) counts towards the
  right report-card slice. **Backwards compatible**: every existing assessment
  derives the same bucket it had before.
- `assessments.services.record_external_result(assessment, student, ...)` — the
  single entry point used by SCORM and LTI to post a result.

### tasks
- `Task.scorm_package` / `Task.lti_resource_link` — a task can *be* an
  interactive activity. Completing it drives the assignee's `TaskAssignment`
  (progress/score/status) automatically (see `scorm.services.sync_result`).
- `Task.launch_url` / `Task.is_interactive` drive the "Launch activity" button on
  the task detail page.

## apps.scorm (self-hosted play)

| URL | Purpose |
|-----|---------|
| `GET /scorm/` | Library + upload form (staff/educators) |
| `POST /scorm/upload/` | Import a `.zip` (unpack + parse manifest) |
| `GET /scorm/<pkg>/launch/` | Player page (scorm-again + resumable attempt) |
| `GET /scorm/<pkg>/content/<path>` | Serve an unpacked file (sanitised, enrolment-scoped) |
| `POST /scorm/runtime/<attempt>/commit/` | Runtime commits CMI JSON → upsert + sync |

- **Runtime**: `scorm-again` (loaded from `SCORM_AGAIN_URL`) exposes
  `window.API` (1.2) / `window.API_1484_11` (2004); the SCO finds it via
  `window.parent`. `runtime.normalise_commit` tolerates flattened / nested /
  `commitObject` payload shapes across editions and versions.
- **Manifest**: `manifest.parse` reads version + launch SCO namespace-agnostically
  (hardened with `defusedxml` when installed).
- **Security**: zip-slip guarded extraction; path-sanitised, per-enrolled-user
  content serving; `commit` is login + attempt-ownership checked. For production,
  serve content from a separate origin (`SCORM_CONTENT_ORIGIN`) via
  `X-Accel-Redirect`/`X-Sendfile` and tighten CSP on the player.

To grade a package, bind it to an `Assessment` of `kind='scorm'` on upload.

## apps.lti (Tool + Platform)

Trust is entirely JWT-based (RS256 + JWKS + nonce/state); all endpoints are
CSRF-exempt and `/lti/` is exempt from the login/onboarding middleware. Manage
registrations in the admin (`/admin/lti/ltiregistration/`); an RSA keypair is
generated on first save and published at the JWKS endpoints.

### Tool role (an LMS launches us)
`/lti/login/` (OIDC init) → `/lti/launch/` (validate id_token → provision/login →
render bound lesson/assessment) → grades pushed back with AGS
(`lti.signals.push_grade_to_platform`). `/lti/jwks/` publishes our tool keys;
`/lti/deep-link/` returns selected content.

### Platform role (we launch a tool)
`/lti/resource/<link>/launch/` → `/lti/platform/authorize/` (issue id_token) →
`/lti/platform/token/` (client-credentials bearer) → `/lti/platform/ags/…`
(receive scores → gradebook) and `/lti/platform/nrps/…` (roster).

### Configuration
- `LTI_PLATFORM_ISSUER` — our issuer id as a platform (defaults to `SITE_URL`).
- `SESSION_COOKIE_SAMESITE=None` + `SESSION_COOKIE_SECURE=True` (HTTPS) for
  iframe launches.
- View `/lti/` for the exact login-init/redirect/JWKS URLs to exchange with an LMS.

## apps.lrs — xAPI / cmi5 Learning Record Store (Phase 4)

A self-hosted LRS (Postgres, no external service — keeps learner data on our
servers). Interactive content emits xAPI **statements** that roll up in one feed.

| URL | Purpose |
|-----|---------|
| `POST/PUT/GET /xapi/statements` | xAPI Statement API (store one/many, query by agent/verb/activity/registration/since/until) |
| `PUT/GET/DELETE /xapi/activities/state` | xAPI State API (resume/bookmark blobs) |
| `GET /xapi/about` | Advertise the xAPI version |
| `GET /lrs/` | Human statements feed (staff/educators) |
| `GET /lrs/cmi5/launch/` · `POST /lrs/cmi5/fetch/<id>/` | cmi5 AU launch + single-use fetch-token swap |

- **Auth**: `Authorization: Basic` (an `LrsCredential`) or `Bearer` (a cmi5
  `Cmi5Session` fetch token); staff sessions for the viewer. `/xapi/` and
  `/lrs/cmi5/` are login-gate-exempt.
- **Emission**: `lrs.services.emit(user, verb, obj, ...)` is called from the
  course player (`experienced`/`completed`), SCORM sync (`completed`/`passed`)
  and an assessment signal (`passed`/`failed`). Verb/activity IRIs use ADL + cmi5
  vocab.

## Interactive course authoring (SCORM-style courses in the hub)

A **Module becomes a playable course**: an ordered list of **segments**
(`learning.ModuleItem`), each a heading, lesson, assessment/quiz or SCORM package.

- **Build**: `/learning/courses/<module>/build/` — educators add/reorder
  (drag-and-drop) / remove segments, mark them required, and *gate* the next
  segment until one is finished.
- **Play**: `/learning/courses/<module>/play/` — learners walk segments in order
  (locked past an unmet gate); lesson bodies render inline, SCORM embeds, quizzes
  link out. Completion of each segment derives from its own record (lesson →
  `ModuleItemProgress`, quiz → `AssessmentAttempt`, SCORM → `ScormAttempt`) and
  emits xAPI. Finishing all required segments issues a **module certificate** and
  refreshes the subject grade.
- **Export**: `/learning/courses/<module>/export/` — download the module as a
  **SCORM 1.2 package** (imsmanifest + a self-contained runtime wrapper), i.e.
  author-your-content-as-SCORM, portable to any LMS.

## Not yet done (next phases)
- Platform-side full 1EdTech certification hardening (exhaustive claim
  validation, token-scope enforcement everywhere, AGS results/paging). Points are
  marked `TODO(cert)` in `apps/lti/platform.py`.
- Richer SCORM export (embedding quiz interactions rather than linking out) and a
  certified LRS backend for heavy xAPI analytics (swap in `lrsql`).
- Vendoring `scorm-again` into `static/` for CSP-locked deployments.
