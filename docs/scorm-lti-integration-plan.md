# SCORM & LTI 1.3 Integration Plan — Learning Hub

**Audience:** developers/architects on the United Church School LMS ("My Learning Hub").
**Scope decided with the team:** LTI 1.3 **both roles** (Platform *and* Tool); SCORM **play + export/author** (and xAPI/cmi5); present **both** a self‑hosted and a managed option.
**Verification key:** ✅ = adversarially fact‑checked in our deep‑research pass (3‑vote). 📘 = sourced from the official spec / vendor docs we gathered but not independently re‑verified in the vote — treat as authoritative‑per‑spec. 🛠️ = engineering design (our recommendation, grounded in the codebase).

---

## 0. Executive summary & recommendation

SCORM and LTI solve **two different problems**, and the hub needs both:

- **SCORM** (and xAPI/cmi5) = a **content‑packaging + in‑browser runtime** standard. A `.zip` of HTML/JS that runs *inside* the hub and reports completion/score to a JS API you expose. Content lives on **your** servers.
- **LTI 1.3** = a **secure cross‑application launch + grade‑exchange** protocol between two separate web apps, using OpenID Connect + signed JWTs. The content lives on **someone else's** server; you exchange identity and grades.

**Recommendation — hybrid, phased:**

1. **Phase 1 — SCORM play (self‑hosted):** `scorm-again` (MIT, maintained) + a small Django app. Cheap, keeps learner data on our servers (POPIA‑friendly), covers ~95% of real content. ✅ library status verified.
2. **Phase 2 — LTI 1.3 Tool side:** `PyLTI1p3` (Django support). Lets external LMSs (Canvas/Moodle/Blackboard) launch into our lessons and lets us post grades back. 📘
3. **Phase 3 — LTI 1.3 Platform side:** custom (no mature Python platform library) — build when there is a concrete external tool to embed (Turnitin, H5P, proctoring). 📘🛠️
4. **Phase 4 — SCORM export + xAPI/cmi5:** generate `imsmanifest.xml` + runtime wrapper for export; add a self‑hosted **SQL LRS** (Apache‑2.0) for cmi5/xAPI. ✅ LRS verified.

Use the **managed** path (Rustici **SCORM Cloud** / **Rustici Engine**) only if we want to eliminate SCORM‑runtime risk entirely and accept a recurring cost + a data‑processor relationship (§7). Both options are fully specified below.

---

## 1. SCORM — standards deep dive

### 1.1 Versions ✅
| | **SCORM 1.2** | **SCORM 2004** (2nd–4th Ed.) |
|---|---|---|
| Global API object | `window.API` | `window.API_1484_11` |
| Method names | **LMS‑prefixed**: `LMSInitialize`, `LMSFinish`, `LMSGetValue`, `LMSSetValue`, `LMSCommit`, `LMSGetLastError`… | **No prefix**: `Initialize`, `Terminate`, `GetValue`, `SetValue`, `Commit`, `GetLastError`… |
| Status model | single `cmi.core.lesson_status` (passed/completed/failed/incomplete/browsed/not attempted) | **split**: `cmi.completion_status` (completed/incomplete) **+** `cmi.success_status` (passed/failed) |
| Score | `cmi.core.score.raw` (0–100 typical) | `cmi.score.raw` **+ `cmi.score.scaled`** — a normalized real in **−1..1** (`real(10,7)`) |
| Suspend data cap | ~4 KB | ~64 KB |
| Sequencing | none | **IMS Simple Sequencing** (rules, navigation, rollup) |

The content (the "SCO") **finds** the API by walking up `window.parent`/`window.opener` looking for `API` or `API_1484_11`. **You provide that object** — that's the whole integration seam.

### 1.2 The run‑time contract ✅
A SCO calls, in order: `Initialize("")` → repeated `GetValue("cmi.…")` / `SetValue("cmi.…","…")` → `Commit("")` (persist) → `Terminate("")` (1.2: `LMSFinish`). Key data‑model elements you must persist: `…lesson_status`/`completion_status`+`success_status`, `…score.raw`/`score.scaled`/`score.min`/`score.max`, `cmi.suspend_data` (opaque resume blob), `cmi.location` (bookmark), `cmi.session_time`/`total_time`.

### 1.3 Packaging (PIF) ✅📘
A SCORM package is a **zip ("PIF")** with `imsmanifest.xml` at the root. The manifest:
- declares the schema/version (in `<metadata>` for 2004 4th Ed.), ✅
- `<organizations>` → the table‑of‑contents tree of items,
- `<resources>` → each `<resource>` has `adlcp:scormType="sco"` (launchable, talks to the API) or `"asset"` (static), the launch file in **`href`**, optional **`xml:base`**. ✅
- 2004 adds `<imsss:sequencing>` rules.

> ⚠️ A refuted claim from research: it is **not** true that exactly "five namespaces are required" on the root `<manifest>` — namespace bindings vary by edition/profile. Validate against the actual ADL test‑suite manifests, not a fixed list. ✅(refutation)

### 1.4 Playing an uploaded package 🛠️
1. **Upload + unzip** the `.zip` to storage; parse `imsmanifest.xml` (e.g. `lxml`) to get version + launch `href`.
2. **Serve content** from a per‑package path with correct MIME types. **Security:** sanitize paths (no traversal), require an authorized, enrolled user, and ideally serve from a **separate origin/subdomain** (e.g. `scorm-content.yourhub.za`) so untrusted package JS can't read your app's cookies/DOM. Use protected media / `X‑Accel‑Redirect`(nginx) / `X‑Sendfile`.
3. **Launch the SCO in an `<iframe>`**; on the parent page expose `window.API` / `window.API_1484_11` via **`scorm-again`** (it implements both runtimes + 2004 sequencing). ✅
4. **Bridge to Django:** configure `scorm-again` with a commit URL; it POSTs the CMI state/score as JSON to your endpoint, which upserts a `ScormAttempt`. Because the player page is **same‑origin** with the hub, normal **session auth + CSRF** work here (unlike LTI). ✅(commit mechanism)
5. **On completion**, map status+score into `assessments.AssessmentAttempt` and recompute `reports.Grade` (§5).

### 1.5 Exporting your content as SCORM 🛠️
Inverse of the above: render the lesson/assessment to static HTML, inject a **runtime wrapper** (e.g. the `pipwerks` SCORM API wrapper — small, MIT ✅, or `scorm-again`'s own bridge) that calls `Initialize/SetValue(score)/Commit/Terminate`, generate a valid `imsmanifest.xml` (Jinja/lxml template with one `<resource scormType="sco">`), and zip it. Validate with the ADL test suite before shipping.

---

## 2. xAPI, cmi5 & the LRS ✅

- **xAPI (Tin Can):** a tracking spec where activities POST **statements** (`{actor, verb, object, result, context}`) to a **Learning Record Store (LRS)** over REST (the Statement API supports `PUT` single‑statement and `POST`; plus State/Activity/Agent‑Profile resources). ✅
- **cmi5** = an xAPI **profile** for launchable, gradeable content (the modern SCORM replacement). The LMS launches an **Assignable Unit (AU)** by URL with params `endpoint, fetch, actor, registration, activityId`. The AU calls the **single‑use `fetch` URL** to get a short‑lived token — it **does not** authenticate directly to the LRS with long‑lived creds. ✅ It then emits a defined statement sequence (`Launched → Initialized → … → Completed/Passed/Failed → Terminated`). ✅
- **LRS option (self‑host):** **Yet Analytics SQL LRS (`lrsql`)** — Apache‑2.0, runs on **PostgreSQL**, xAPI‑conformant. ✅ Good fit since we already run Postgres.

> Note: `scorm-again` is SCORM‑only — **no xAPI/cmi5** (it's on their roadmap; AICC support was removed). ✅ So cmi5/xAPI needs a *separate* LRS regardless of plan.

---

## 3. LTI 1.3 + LTI Advantage 📘

LTI 1.3 replaces the old OAuth1 signing of LTI 1.1 with **OpenID Connect + JWTs signed RS256**. Two parties:
- **Platform** = the LMS that initiates the launch and owns the gradebook/roster.
- **Tool** = the external app being launched.

Our hub will be **both**.

### 3.1 The launch flow (resource‑link launch) 📘
1. **OIDC third‑party initiated login:** the **Platform** hits the **Tool's login‑init URL** with `iss, login_hint, target_link_uri, client_id, lti_message_hint, deployment_id`.
2. The **Tool** redirects to the **Platform's OIDC authorization endpoint** with `response_type=id_token, scope=openid, response_mode=form_post, prompt=none, client_id, redirect_uri, login_hint, state, nonce`.
3. The **Platform** authenticates the user and **`form_post`s a signed `id_token` (JWT)** back to the Tool's `redirect_uri`.
4. The **Tool validates** the JWT: signature against the **Platform's JWKS** (public keys), plus `iss`, `aud`(=client_id), `exp/iat`, `nonce`, and `deployment_id`. The JWT carries the LTI claims: message type, version, **roles**, **context** (course), **resource_link**, **custom** params, and the **AGS/NRPS service endpoints**.

### 3.2 LTI Advantage services 📘
- **Deep Linking 2.0** — content selection: the Platform launches the Tool in "deep‑link" mode; the Tool returns a **signed JWT** with `content_items` to the Platform's `deep_link_return_url`. (Used when an educator picks *which* tool content to embed.)
- **AGS (Assignment & Grade Services v2.0)** — gradebook sync: **line items** (columns), **scores** (`POST` a score), **results** (read). OAuth2 scopes: `…/lineitem`, `…/lineitem.readonly`, `…/score`, `…/result.readonly`.
- **NRPS (Names & Role Provisioning v2.0)** — roster: a memberships endpoint; scope `…/contextmembership.readonly`.

Services use **OAuth2 `client_credentials`** where the client secret is a **signed JWT assertion**; the caller gets a short‑lived bearer token scoped to the service.

### 3.3 What differs Platform vs Tool 📘🛠️
| Responsibility | As **Tool** (Phase 2) | As **Platform** (Phase 3) |
|---|---|---|
| OIDC login‑init endpoint | **host** (receive) | call the tool's |
| OIDC authorization endpoint | call the platform's | **host** (issue `id_token`) |
| Sign the launch `id_token` | no (verify it) | **yes** (RS256 with our private key) |
| JWKS (public keys) | **host** tool keys | **host** platform keys |
| OAuth2 token endpoint (for services) | call it | **host** it |
| AGS/NRPS | **call** (post our grade up) | **host** (receive grades, serve roster) |
| Identity | map `iss+sub` → local user (provision/login) | assert our user to the tool |

---

## 4. Library & service landscape

| Need | Self‑hosted pick | Status |
|---|---|---|
| SCORM 1.2 + 2004 runtime (play) | **`scorm-again`** (jcputney) | ✅ MIT, TypeScript, v3.0.x, **actively maintained** (to 2026‑05), implements both runtimes + 2004 sequencing, commits over HTTP via `lmsCommitUrl`. **No xAPI/cmi5.** |
| SCORM export wrapper | **`pipwerks` SCORM API wrapper** / `simplify-scorm` | ✅ MIT, small, stable (low‑churn) |
| xAPI/cmi5 LRS | **Yet Analytics SQL LRS (`lrsql`)** | ✅ Apache‑2.0, PostgreSQL, xAPI‑conformant |
| LTI 1.3 **Tool** | **`PyLTI1p3`** (dmitry‑viskov) + Django adapter | 📘 De‑facto Python LTI 1.3 **Tool** library; covers message launch, **Deep Linking, AGS, NRPS**; has Django/Flask adapters. Verify current maintenance before committing. |
| LTI 1.3 **Platform** | **custom** (`PyJWT`/`authlib` + your endpoints) | 📘🛠️ No mature open‑source Python **Platform** library — this side is bespoke. Budget for it. |
| Managed SCORM/xAPI/cmi5 | **Rustici SCORM Cloud** (SaaS) or **Rustici Engine** (self‑host license) | 📘 Import‑course / registration / launch / results‑postback REST API; certified runtime; US/EU hosting. |

**Key management** 🛠️: generate an RSA keypair per role; publish public keys at a **JWKS** endpoint (`kid`‑tagged) so rotation is seamless; keep private keys in env/secrets, never in the repo. Canvas/Moodle register a tool either by **Dynamic Registration** (automated) or **manual** (you give them: login‑init URL, redirect URI(s), tool JWKS URL, target_link_uri; they give you: issuer, client_id, auth/token/JWKS URLs, deployment_id).

---

## 5. Concrete Django integration design 🛠️

Two new apps (keeps interop isolated from core LMS): **`apps/scorm`** and **`apps/lti`**. A self‑hosted LRS (`lrsql`) runs as a **separate service**, not a Django app.

### 5.1 SCORM models
```text
scorm.ScormPackage
  lesson        FK→learning.Lesson (or OneToOne)
  title, version('1.2'|'2004'), launch_href, storage_root
  manifest_identifier, uploaded_by FK→User, created_at

scorm.ScormAttempt            # one learner's registration against a package
  package FK, student FK→User, subject FK→accounts.Subject
  completion_status, success_status, lesson_status   # cover 1.2 + 2004
  score_raw, score_scaled, score_min, score_max
  total_time, session_time, location(bookmark)
  suspend_data  TextField                            # opaque resume blob
  cmi_data      JSONField                            # full cmi tree (source of truth)
  attempt_no, updated_at
  → unique(package, student, attempt_no)
```

### 5.2 LTI models
```text
lti.LtiRegistration           # one trust relationship
  role('tool'|'platform'), issuer, client_id
  auth_login_url, auth_token_url, key_set_url   # the OTHER party's endpoints
  private_key, public_key_jwks                  # OUR keypair for this reg
lti.LtiDeployment             reg FK, deployment_id
lti.LtiResourceLink           # binds a launch to internal content / external tool
  deployment FK, resource_link_id
  lesson FK→learning.Lesson (Tool side)  |  external_tool_url + custom (Platform side)
lti.LtiLineItem               # AGS gradebook column ↔ our grade
  resource_link FK, subject FK, assessment FK→assessments.Assessment (nullable)
  max_score, ags_lineitem_url
lti.LtiUser                   reg FK, sub, local_user FK→User   # identity map
```

### 5.3 Endpoint surface
```text
# SCORM (same-origin → session auth + CSRF OK)
GET  /scorm/<pkg>/launch/                player page (iframe + scorm-again config)
GET  /scorm/<pkg>/content/<path>         unpacked content (protected, sanitized, ideally separate origin)
POST /scorm/runtime/<attempt>/commit/    scorm-again posts CMI/score JSON

# LTI — Tool role (cross-origin → CSRF-EXEMPT, JWT/OAuth, SameSite=None launch cookie)
GET/POST /lti/login/                     OIDC third-party login init
POST     /lti/launch/                    redirect_uri: validate id_token → provision/login → render content
GET      /lti/jwks/                      our tool public keys
POST     /lti/deep-link/                 deep-linking response (signed JWT back)
#        AGS score posting is OUTBOUND (we call the platform)

# LTI — Platform role (cross-origin → CSRF-EXEMPT)
GET      /lti/platform/authorize/        issue signed id_token (form_post)
POST     /lti/platform/token/            OAuth2 client_credentials → scoped bearer
GET      /lti/platform/jwks/             our platform public keys
GET/POST /lti/platform/ags/...           external tools post scores here → reports.Grade
GET      /lti/platform/nrps/...          serve course roster
```

### 5.4 How grades flow into the existing gradebook
- **SCORM:** `commit` → `ScormAttempt`. On `completed`/`passed`, **upsert** an `assessments.AssessmentAttempt` (score from `score_raw` or `score_scaled×max`) for the linked lesson's assessment, then call the existing `reports.services.compute_grade()` so it lands in report cards, certificates and analytics — **no new gradebook.**
- **LTI as Tool:** learner works in our hub → we `POST` an AGS **score** to the launching LMS's line item, *and* store a local `AssessmentAttempt`.
- **LTI as Platform:** external tool `POST`s a score to our `/lti/platform/ags/` → write `LtiLineItem` result → `AssessmentAttempt` → `reports.Grade`.

### 5.5 Security must‑knows 🛠️
- **LTI endpoints are cross‑origin** → `@csrf_exempt`; trust comes from **JWT signature + nonce + state**, never session/CSRF. The launch lands via `form_post` from another site, so the launch session cookie needs **`SameSite=None; Secure`** (PyLTI1p3 ships a cookie/state fallback for browsers that drop third‑party cookies). Add these paths to the middleware **exempt lists** (we already keep `_EXEMPT_PREFIXES` for `LoginRequiredMiddleware`/`OnboardingMiddleware`).
- **SCORM content is untrusted JS** → serve from an isolated origin, sanitize paths, scope every file to an enrolled user, set a tight CSP on the player page.
- **Keys** → JWKS with `kid` rotation; private keys in secrets; one keypair per registration (or a shared platform keypair).

---

## 6. Plan A — Fully self‑hosted

**Stack:** `scorm-again` (play) + `pipwerks` (export) + custom `apps/scorm` + `apps/lti` + `PyLTI1p3` (Tool) + custom Platform endpoints + self‑hosted `lrsql` for cmi5/xAPI.

- **Effort:** High. SCORM play ≈ 1–2 wks; LTI Tool ≈ 1–2 wks; LTI Platform ≈ 3–4 wks (bespoke); export + LRS ≈ 1–2 wks.
- **Cost:** Infra only (no per‑registration fees). `lrsql` free (Apache‑2.0).
- **Data residency:** ✅ Everything stays on our Postgres/servers — best for **POPIA**.
- **Maintenance/conformance:** We own runtime correctness, security and any **1EdTech certification** (paid, optional). No vendor SLA.
- **Best when:** data residency + zero recurring cost matter most and we have engineering capacity.

## 7. Plan B — Managed services

**Stack:** Rustici **SCORM Cloud** (SaaS) **or** **Rustici Engine** (self‑host license) for SCORM/xAPI/cmi5; `PyLTI1p3` still does the LTI **Tool** glue; LTI **Platform** still custom.

- **How it connects:** our Django calls SCORM Cloud's REST API to **import a course**, **create a registration** (returns a hosted launch URL we iframe), and **receive results** via **postback** or polling → write into `ScormAttempt`/`AssessmentAttempt`. 📘
- **Effort:** Lower for SCORM/xAPI (no runtime to build/maintain); LTI effort unchanged.
- **Cost:** Recurring, tiered by registrations/active learners (has a small free/trial tier). 📘
- **Data residency:** Learner data transits a **third‑party processor**; choose an EU/region deployment or **Rustici Engine self‑hosted** to satisfy POPIA. 📘
- **Maintenance/conformance:** Rustici owns the certified SCORM/xAPI runtime + edge‑case conformance. Vendor SLA.
- **Best when:** we want to de‑risk the gnarly SCORM/xAPI runtime fast and accept recurring cost + a DPA.

### Side‑by‑side
| | **A — Self‑hosted** | **B — Managed** |
|---|---|---|
| SCORM runtime | `scorm-again` (build) | SCORM Cloud/Engine (buy) |
| xAPI/cmi5 | `lrsql` (self‑host) | included |
| LTI Tool / Platform | PyLTI1p3 / custom | PyLTI1p3 / custom (same) |
| Recurring cost | none | yes (tiered) |
| Data residency | ✅ full control | ⚠️ processor / pick region or Engine |
| Conformance burden | us | vendor (SCORM/xAPI) |
| Time‑to‑first‑play | slower | faster |

---

## 8. Recommended path for the UCS LMS 🛠️

Given POPIA + cost sensitivity + existing Postgres/Django strength:

1. **Phase 1 (now):** self‑host **SCORM play** with `scorm-again` + `apps/scorm`, wired into `learning.Lesson` and `reports.Grade`. Highest value, lowest risk, no recurring cost.
2. **Phase 2:** **LTI 1.3 Tool** via `PyLTI1p3` so our content is consumable by partner LMSs and grades sync out.
3. **Phase 3:** **LTI 1.3 Platform** (custom) when a concrete external tool needs embedding.
4. **Phase 4:** **SCORM export** + **cmi5/xAPI** via `lrsql`.
5. **Re‑evaluate Plan B** only if SCORM conformance edge cases become a time sink — then offload *just the runtime* to Rustici Engine (self‑hosted, keeps residency).

Next deliverable when we start building: a migration‑ready `apps/scorm` (models above) + a `scorm-player.html` template that loads `scorm-again` and points its commit URL at `/scorm/runtime/<attempt>/commit/`.

---

## 9. Sources

**SCORM runtime/packaging (✅ verified):**
- Rustici — Run‑Time Reference: https://scorm.com/scorm-explained/technical-scorm/run-time/run-time-reference/
- Rustici — Manifest structure: https://scorm.com/scorm-explained/technical-scorm/content-packaging/manifest-structure/
- Rustici — SCORM versions: https://scorm.com/scorm-explained/business-of-scorm/scorm-versions/
- ADL SCORM‑2004‑4ed Test Suite (sample manifest): https://github.com/adlnet/SCORM-2004-4ed-Test-Suite

**xAPI / cmi5 / LRS (✅ verified):**
- cmi5 spec (current): https://github.com/AICC/CMI-5_Spec_Current/blob/quartz/cmi5_spec.md
- cmi5 AU launch flow: https://aicc.github.io/CMI-5_Spec_Current/flows/au-flow.html
- cmi5 Technical 101: https://xapi.com/cmi5/cmi5-technical-101/
- xAPI communication spec: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Communication.md
- Yet Analytics SQL LRS: https://www.sqllrs.com/

**Open‑source SCORM player (✅ verified):**
- scorm-again (repo): https://github.com/jcputney/scorm-again — (docs) https://jcputney.github.io/scorm-again/ — (releases) https://github.com/jcputney/scorm-again/releases
- pipwerks SCORM API wrapper: https://github.com/pipwerks/scorm-api-wrapper
- simplify-scorm: https://github.com/gabrieldoty/simplify-scorm

**LTI 1.3 / LTI Advantage (📘 spec‑sourced):**
- LTI 1.3 Implementation Guide: https://www.imsglobal.org/spec/lti/v1p3/impl
- IMS Security Framework: https://www.imsglobal.org/spec/security/v1p0
- LTI AGS v2.0: https://www.imsglobal.org/spec/lti-ags/v2p0
- 1EdTech LTI Implementation Guide: https://standards.1edtech.org/lti/specifications/guides/implementation_guide/implementation-guide

**Python LTI + managed SCORM (📘 spec/vendor‑sourced):**
- PyLTI1p3 (PyPI): https://pypi.org/project/PyLTI1p3/ — (repo) https://github.com/dmitry-viskov/pylti1.3 — (health) https://snyk.io/advisor/python/pylti1p3
- SCORM Cloud pricing: https://rusticisoftware.com/products/scorm-cloud/pricing/
- SCORM Cloud registration API: https://cloud.scorm.com/docs/api_reference/v1/registration/
- Rustici Engine: https://rusticisoftware.com/products/rustici-engine/ — (deployment/residency) https://rusticisoftware.com/products/deployment-options/

*Research method: 5 search angles → 27 sources fetched → 124 claims extracted → 25 adversarially verified (24 confirmed, 1 refuted). LTI/Rustici specifics carry the 📘 marker: drawn from the official sources above but not re‑verified in the vote — confirm against the linked specs at build time.*
