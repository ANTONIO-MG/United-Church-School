# Error codes, the dictionary and the error log

For developers and administrators. Learners, parents and educators never see any
of this — every diagnostics view returns **404** for them.

| Where | What |
|---|---|
| `/diagnostics/` | The error log — one row per distinct problem, with counts |
| `/diagnostics/dictionary/` | Every code, why it happens, and how to fix it |
| `/diagnostics/dictionary.json` | The same, as JSON for tooling |
| `/diagnostics/export/` | The log as CSV |
| `/admin/diagnostics/errorevent/` | The same log in the Django admin |
| `manage.py errorcheck` | Audits the catalog against the source; exits non-zero on a problem |

---

## Reading a code

    CERT-8001
    ────┬─── ┬───
        │    └─ 8xxx = rendering / storage
        └────── certificates

**The prefix says where. The first digit of the number says what kind.** The
digit means the same thing in every domain, so `CERT-8001` and `FIN-8001` are
both "something failed while producing or saving a document" without looking
anything up.

### Cause classes

| Range | Class | Meaning |
|---|---|---|
| `1xxx` | Input / validation | Malformed or incomplete request. Almost always user-fixable. |
| `2xxx` | Permission / access | Authenticated, but not allowed to do this. |
| `3xxx` | Missing / not found | The thing being acted on does not exist. |
| `4xxx` | Conflict / business rule | Well-formed, but the rules forbid it now. |
| `5xxx` | External service | A third party failed or was unreachable. |
| `6xxx` | Data integrity | Stored data is inconsistent with what the code needs. |
| `7xxx` | Configuration | A setting, key or dependency is missing on this deployment. |
| `8xxx` | Rendering / storage | Producing or persisting a file or document failed. |
| `9xxx` | Unexpected | Unhandled. Every one of these is a bug to be classified. |

### Domains

`SYS` platform · `AUTH` sign-in · `USER` profiles & enrolment · `CHAT` messaging ·
`MEET` calls & attendance · `NOTF` notifications · `FEED` activity feed ·
`MAIL` e-mail · `LRN` lessons · `ASMT` assessments · `CERT` certificates ·
`RPRT` grades & exports · `ANLT` analytics · `TASK` tasks · `SHOP` store ·
`FIN` invoices & payments · `FILE` uploads · `INTG` Microsoft Teams ·
`LTI` · `SCRM` SCORM · `H5P` · `LRS` xAPI · `AI` · `SCHD` jobs · `HUB` dashboard

Every entry answers four questions — **what** went wrong, **why** it happens,
what a **developer** should check, and what to tell the **user**. A code with no
remedy is just a number, and the test suite enforces that all four are filled in
and that the developer fix names somewhere to look.

---

## Reporting an error from code

```python
from core.errors import capture, errorcode, fail, note, report
```

| Helper | Use it when | Raises? |
|---|---|---|
| `note(code, request, **ctx)` | An expected refusal you handled yourself | no |
| `fail(code, msg, request, **ctx)` | You want to record *and* raise it | yes |
| `capture(code, request)` | A block whose failure you want tagged | yes (`reraise=False` to swallow) |
| `report(code, exc, request)` | You already caught it and want it logged | no |
| `@errorcode(code)` | A whole view or service function | yes |

```python
# An expected refusal — correct behaviour, but a spike means something upstream broke.
note('CHAT-2001', request, group=group.pk)

# Record it and raise it; the message ends with "(CERT-1001)" for the user to quote.
fail('CERT-1001', 'This certificate has no holder name', request, certificate=cert.pk)

# Tag whatever escapes the block.
with capture('CERT-8001', request, context={'certificate': cert.pk}):
    png = certificate_render.render_png(data)

# One source of a page failing must not blank the page.
with capture('FEED-9001', reraise=False, context={'source': 'tasks'}):
    add_tasks()
```

Context is stored as JSON and **redacted**: any key containing `password`,
`token`, `secret`, `api_key`, `client_secret`, `authorization`, `cookie` or
`csrf` is replaced with `[redacted]` before it is written.

Reporting never raises. An error logger that throws turns a handled problem into
a 500, so every helper swallows its own failures.

---

## Errors nobody tagged

Coverage does not depend on hand-tagging all ~300 exception handlers. Three
layers catch the rest:

1. **The logging handler** (`apps/diagnostics/handlers.py`) turns every existing
   `logger.exception(...)` / `logger.error(...)` / `logger.warning(...)` into a
   catalogued event. The domain comes from the module that raised (falling back
   to the logger's name), and the cause class from the exception type — so an
   untagged `OSError` in `apps.reports.certificates` still arrives as an `8xxx`
   certificates error.
2. **The middleware** (`ErrorCaptureMiddleware`) records anything that escapes a
   view as `SYS-9001`, with a **reference** the user can quote to support. It
   never suppresses the exception; Django still handles the response. `Http404`
   and `PermissionDenied` are ignored — they are control flow, and logging them
   would bury real faults.
3. **`manage.py errorcheck`** reports which modules still have untagged error
   sites, so the gap is measurable and can be worked down.

To tag a log call without changing the code around it:

```python
logger.error('delivery failed', extra={'error_code': 'MAIL-5001'})
```

---

## How the log behaves

Events are **deduplicated on a fingerprint** of code + module + function +
exception type, and carry a `count`. A loop that fails ten thousand times is one
row saying `10000`, not ten thousand rows burying everything else. Only the most
recent traceback is kept, for the same reason.

A **resolved error that happens again is reopened automatically** — silently
re-closing it is how a "fixed" bug stays broken in production.

Triage from the event page: *Resolved*, *Acknowledged*, *Ignored*, *Reopen*, plus
a free-text developer note.

---

## Adding a code

1. Add an `_e(...)` entry to `apps/diagnostics/catalog.py` in the right domain
   section, choosing the number from the cause class.
2. Fill in all four fields. The tests will fail if any is missing, too terse, or
   if the developer fix does not name a module, setting or file to look at.
3. Reference it from the code with one of the helpers above.
4. Run `manage.py errorcheck` — it fails if a code is used but not documented.

Codes are permanent once shipped: they end up in support tickets and screenshots.
Reword an entry freely; do not renumber one.
