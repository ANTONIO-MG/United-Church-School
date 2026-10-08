# Live sessions — the calendar, the recording pipeline, the follow-up

Scheduling a class on the platform creates a Microsoft Teams meeting, tells exactly the
right people in their own time zone, records itself, files the recording and its
transcript into a predictable OneDrive folder, publishes it as a re-watchable
past session, and writes the next session's agenda. This document is how that
works and what has to be configured for each stage.

[docs/TEAMS_INTEGRATION.md](TEAMS_INTEGRATION.md) covers the Microsoft Graph auth
model and the Entra app registration. Read that first; this builds on it.

```
   Schedule on the platform
        │
        ├─► Graph: create onlineMeeting  (recordAutomatically = true)
        ├─► Graph: create Outlook event, invite licensed staff only
        ├─► Draw the thumbnail (Pillow)
        ├─► Open the attendance register (ClassSession)
        ├─► Put it on the module schedule (ModuleMaterial, kind=live)
        └─► Notify the audience  ──►  24h reminder  ──►  30m reminder
                                                              │
                                                        session runs
                                                              │
   ┌──────────────────────── after-class pipeline ────────────┴──────────┐
   │  polling → filing → summarising → uploading → published             │
   │     │         │           │            │           │                │
   │  Graph:    OneDrive:   recap +      YouTube      recording on the    │
   │  is the    move the    attendance   (unlisted,   module schedule,    │
   │  recording video,      reconcile,   quota-       audience notified   │
   │  ready?    write .vtt  summary.md   paced)                           │
   └──────────────────────────────────────────────────────────────────────┘
                                    │
                     apps.livesessions.ai_followup (admin Claude layer)
                     full summary · next agenda · action items → Tasks
```

## One calendar, many sources

The platform had two calendar aggregations — the myhub events feed and, briefly,
a second one inside the live-session work — and they disagreed. The old feed
showed only meetings you hosted or were *individually* invited to, so a module
class never reached the calendar of the students it was for.

There is now one aggregation, `apps.livesessions.sources`, and every surface
renders from it: the month grid, the day view, `myhub:events`, both JSON feeds
and the exported `.ics`. Adding a source there makes it appear everywhere.

| Source | What it contributes | Scoped by |
|---|---|---|
| `session` | live sessions | `livesessions.audience` |
| `academic` | tests, exams, deadlines (`learning.CalendarEvent`) | the reader's institutions |
| `event` / `reminder` | the practice diary and personal reminders (`myhub.Event`) | owner, or institution-wide |
| `task` | task deadlines | the reader's own assignments |
| `lesson` | lessons publishing | the reader's modules |
| `assessment` | assessment closing dates | the reader's modules |
| `external` | imported Google / Outlook / Apple events | the reader's own connections |

Each source scopes itself *before* returning, so a caller renders what it is
handed without re-checking anything. One source raising does not blank the
calendar — it is logged and the rest still render. The legend on the month view
doubles as a filter (`?show=session,academic`), so a filtered month is a
shareable link.

## Connecting an outside calendar

Both directions run over plain **iCalendar feeds**, not OAuth. Google, Microsoft
365 and Apple each publish a private `.ics` address and each subscribe to one, so
a feed needs no consent screen, no per-user token refresh, no API quota and no
Google verification review — and, importantly, it **cannot write** to anybody's
calendar, which is the right authority for something the platform only needs to read.

**Export — the school calendar into theirs.** Settings → Connected calendars gives
each person a private feed URL (`/calendar/feed/<token>.ics`). It is deliberately
unauthenticated and addressed by a secret token, because that is the only thing
Google and Outlook can subscribe to: they fetch it from their own servers, with
no session and no way to sign in. The token is therefore the credential, which is
why **Reset this link** exists — rotating it instantly revokes every device and
every person the old URL reached. The prefix `/calendar/feed/` is the only part
of `/calendar/` exempt from the site-wide login gate.

Events the user *imported* are excluded from their own export. Publishing them
back would loop them into the calendar they came from as duplicates.

**Import — their calendar into the platform.** Paste the private `.ics` address from
Google ("secret address in iCal format"), Outlook ("publish a calendar") or
iCloud. Events import read-only as busy time and refresh every 30 minutes
(`calendar-subscriptions`). Each refresh **replaces** its window wholesale, so a
meeting deleted in Google disappears here too.

This matters most for educators: `services.free_slots(..., for_user=...)`
subtracts their connected calendar, so "when can I book this class?" accounts for
the lecture already in their own diary rather than booking straight over it. An
event the source calendar marks `TRANSPARENT` (free) is shown but never blocks.

A feed that fails five times running is switched off and its owner notified —
the usual cause is a link they revoked, and only they can issue a new one.

### The ICS layer

`apps.livesessions.ics` is hand-rolled rather than pulling in `icalendar` +
`recurring-ical-events`, because what an imported feed is asked for is narrow
(*when is this person busy*) and this project keeps its dependency list short.

Supported: line unfolding, `DTSTART`/`DTEND`/`DURATION`, `DATE` and `DATE-TIME`,
`TZID` and UTC, `SUMMARY`, `LOCATION`, `UID`, `STATUS`, `TRANSP`, `EXDATE`, and
simple `RRULE` (`FREQ` daily/weekly/monthly/yearly with `INTERVAL`, `COUNT`,
`UNTIL`, `BYDAY`). Not supported: `BYSETPOS`/`BYMONTHDAY` and the rarer rule
parts, `VTODO`/`VJOURNAL`, alarms, attendees. **An event using an unsupported
rule still imports — it simply appears once instead of repeating.** That is the
right way to be wrong: the overlay under-reports busy time rather than inventing
a phantom booking on a day that is actually free.

Recurrences expand only inside the requested window and are hard-capped, so a
feed containing "every weekday forever" costs the same as any other.

**The fetch is treated as hostile,** because the URL comes from a form. Without
guards that is an SSRF hole — someone could point it at cloud metadata
(`169.254.169.254`) or an internal service and read the response back out of
their calendar. So: `http`/`https`/`webcal` only, every resolved address checked
against the private/loopback/link-local ranges, redirects followed manually with
the same check each hop, a body cap and a timeout.

### Why not OAuth?

Worth knowing what was traded away. Native Google Calendar / Microsoft Graph
delegated access would allow **writing** to a user's calendar and true two-way
sync. It also needs a per-user consent flow, refresh-token storage and rotation,
Google's verification review for sensitive scopes, and conflict resolution for
edits made on both sides. For a schedule the platform *owns* and the user only reads,
the feed is the better trade.

One exception already exists: for licensed staff the platform does create real
Outlook events through Graph (`services.ensure_calendar_event`), because there
the app is already authenticated app-only and the invite has to carry the Teams
join link.

## Who sees what

One rule, in `apps.livesessions.audience`, used by **both** the notifier and the
calendar so they cannot drift apart:

| Audience | Notified & visible to |
|---|---|
| `everyone` | every active account |
| `institution` | everyone enrolled at, or teaching at, that institution |
| `programme` | everyone enrolled on, or teaching on, that programme |
| `cohort` | that intake only |
| `module` | everyone enrolled on, or teaching, that module offering |
| `private` | named invitees only — this is also how a one-on-one works |

Named invitees are **additive**: you can invite one extra person to a module
class and they will be told and will see it.

The one deliberate asymmetry is supervisory. Admin and staff *see* every session
at every institution — that is what makes the calendar usable for finding a free
slot — but they are not *notified* about every session. Educators are the same
for the modules they teach. So: being told is always a subset of being able to
see, never the reverse.

## Time zones

`UserSettings.timezone` is set by the user under Settings → Preferences.
`UserPreferenceMiddleware` activates it per request, so every template time is
already local — no per-view conversion anywhere. Reminders and invite e-mails are
rendered **once per recipient** (`reminders.local_when`) and name the zone, so a
class at 14:00 SAST reads as 13:00 (WAT) to a candidate in Lagos.

Stored data is always UTC (`USE_TZ = True`). Only the display moves.

## Reminders

Leads are configured in Live session settings (`reminder_leads`, default
`1440,30` — 24 hours and 30 minutes). The `session-reminders` job runs every five
minutes.

Whether a reminder has been sent is a **row** in `SessionReminder`, not an
inference from the clock. The job ticks far more often than the leads it serves,
so "is it about 30 minutes before?" would fire repeatedly; "has this person been
reminded at the 30-minute lead?" fires once, and stays correct if the job is down
for an hour and catches up late. Rescheduling a session clears the ledger so
everyone is told again against the new time.

## The OneDrive tree

```
<root>/<INSTITUTION>/<PROGRAMME>/<MODULE>/<YYYY-MM-DD Session title>/
    2026-03-04 Deferred tax workshop.mp4
    2026-03-04 Deferred tax workshop-transcript.vtt
    2026-03-04 Deferred tax workshop-summary.md
    2026-03-04 Deferred tax workshop-session-pack.md
    2026-03-04 Deferred tax workshop-thumbnail.jpg
```

`<root>` is `LiveSessionSettings.onedrive_root` (set it to e.g. `UCS Sessions` in the admin; a blank value falls back to `UCS Sessions`).
Levels that do not apply are left out — a platform-wide briefing lands under
`General/` rather than in a chain of "None" folders.

By default each session is filed in **its own organiser's** drive, which is where
Teams put the recording anyway, so the move is metadata-only and no bytes travel.
Set `onedrive_owner_upn` to keep the whole archive in one drive instead (one
place, one backup, one retention policy) at the cost of a server-side copy.

> **Not Google Drive.** Teams recordings are created in OneDrive/SharePoint;
> there is no Microsoft path that writes them to Google Drive. Mirroring them
> there would mean downloading and re-uploading every recording through this
> server. The transcript and summary live beside the video for the same reason —
> one folder, one thing to find, one thing to back up.

## YouTube — and its quota

Students join Teams **anonymously** and have no Microsoft account, so a OneDrive
link only plays for them while an anonymous sharing link exists — and plenty of
tenants forbid those outright. An unlisted YouTube video plays for anyone with
the link, embeds cleanly, and streams adaptively on a phone. That is why it is
here.

**The quota is the constraint.** `videos.insert` costs **1,600 units** of a
default **10,000/day** allowance: about **six sessions a day**, then every
further attempt fails until midnight US/Pacific. So the pipeline *asks* before it
uploads (`youtube.quota_available()`) and leaves the session queued if there is
no room, retrying on the next tick. Nothing is lost and nobody waits — the
session is already watchable through its OneDrive link, and the YouTube id simply
replaces it when it lands.

A quota increase means applying to Google for an audit and takes weeks. Plan for
it; the pacing is permanent, not a stopgap.

To switch it on:

1. `pip install google-api-python-client google-auth google-auth-oauthlib`
   (the commented block in `requirements.txt`).
2. Google Cloud project → enable **YouTube Data API v3** → create an OAuth
   client (type *Desktop app*).
3. Exchange a one-time consent code for a **refresh token** on the
   `https://www.googleapis.com/auth/youtube.upload` scope.
4. Put the three values in `.env` (`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`,
   `YOUTUBE_REFRESH_TOKEN`).
5. Tick **YouTube enabled** in Live session settings.

Until all five are done the platform behaves exactly as before, serving the
OneDrive link.

## Thumbnails

One background image is configured once (Live session settings →
*Thumbnail background*, ideally 1280×720). Every session's card is that image
with its own details drawn on top: session kind, title, programme | module, the
week or test it covers, and the date and time. A gradient scrim keeps the text
readable over a busy photograph. The same JPEG is used on the platform card, the
schedule row and the YouTube thumbnail.

No background configured? The card is drawn on a flat brand panel — a plain
thumbnail is a much smaller problem than a session that could not be created
because an image was.

Redraw them all after changing the background or the colours:

```bash
manage.py generate_session_thumbnails --all
```

## Identity — who actually joined

**Microsoft offers no supported way to pre-fill an anonymous attendee's display
name.** Teams shows its own "Enter your name" box, and whatever the student types
is all the attendance report carries. Matching that on e-mail alone finds a
minority of a class. (True identity would mean giving every candidate an Entra
guest account — sign-in friction, admin overhead, and the opposite of the
anonymous-join model.)

So the platform does not rely on Teams for identity. It settles it before Teams ever
sees the student, and then matches the report back afterwards.

**1. The identified hand-off.** `/calendar/sessions/<pk>/join/` is the only route
into a live room, and it is behind the login gate. At that moment we know exactly
who is going in — first name, surname, e-mail, from their own profile — and write
it to a `SessionJoin` row before redirecting to Teams. That row is authoritative
and does not depend on anything the student types.

Clicking is not attending: the row starts no clock and marks nobody present. It
opens the register entry at zero seconds; presence is still *measured*, by the
Graph report and the page heartbeat.

**2. The name nudge.** The session page shows the exact name their attendance is
filed under and copies it to the clipboard as they leave, so the Teams name box
is a paste rather than a retype. A nudge, not a guarantee — the hand-off above is
what the register actually relies on.

**3. Roster-bounded matching** (`apps.livesessions.identity`). For each session
the candidate set is bounded to its own audience plus everyone who clicked
through. Inside a few dozen people a name becomes a usable key. Matching runs
strongest-evidence-first:

| Order | Key | Why it is trusted |
|---|---|---|
| 1 | e-mail address | exact, unambiguous |
| 2 | Microsoft UPN (`Person.ms_upn`) | the identity a licensed user carries |
| 3 | a remembered alias | a correction an educator already made |
| 4 | normalised name, roster-scoped | unique *within this session* |

Normalisation case-folds, strips accents, bracketed decoration and emoji, and
collapses whitespace, so `"  Thabo  MOKOENA (GR10) 🎓 "` and `"thabo mokoena"`
are the same key. **A name that two people in the roster answer to is refused,
not guessed** — a wrong name on a register is worse than a blank one.

**4. Corrections stick.** Whatever cannot be resolved is listed on the session
register (`/calendar/sessions/<pk>/register/`) with the roster to attach it to.
Attaching writes a `TeamsIdentityAlias`, so the student who joins as "Tebza 📱"
every week is corrected **once** and matches by themselves from then on. An alias
already belonging to someone else is never silently reassigned.

**5. Names reach the summary.** The Claude session pack and the filed
`summary.md` carry a *Who attended* roster — real names, e-mails and minutes —
drawn from the platform's own register rather than from what people typed. The
model is told it may attribute a question to a named person when the transcript
makes the speaker clear, and is explicitly told never to put an e-mail address in
the prose or to guess who spoke.

## Attendance

Microsoft Graph is **authoritative** for a Teams class: it reports exactly how
long each person was in the call, where the platform's own heartbeat can only see
how long the launch page stayed open. Reported seconds replace accrued ones and
the status is re-derived against the session's `min_attendance_pct` — attending
12 minutes of a 60-minute class does not become "present" just because Graph saw
the person. Manual educator marks are never overwritten.

Graph is **not** authoritative for identity — see *Identity* above for how a
report of typed-in names is resolved back to real candidates.

For a **one-on-one** there is no class register to file, so the attendance record
is sent to the attendee personally instead.

## The AI follow-up

After a session is published, `apps.livesessions.ai_followup` reads the
transcript and the automatic recap and writes:

1. a full written summary, for someone who missed the class;
2. the **agenda for the next session**, built from what was left unfinished;
3. **action items**, split between candidates and the educator, which become real
   `tasks.Task` rows so they appear in "My Tasks" and are swept by the existing
   deadline-reminder job.

Three constraints, deliberately:

* **Admin layer only.** It runs on `apps.ai_assistant.admin_ai` — the paid,
  token-billed Claude tier reserved for admins and staff — under the platform's
  own identity, never on a student's or an educator's account, and never inside a
  request. It is a background job precisely so nobody's page waits on it and no
  student's session can spend admin tokens.
* **Filed, not broadcast.** Output goes back where the rest of the session's
  material lives: the session's OneDrive folder, an `AiReport` on the module, and
  the module's Documents tab.
* **Never destructive.** If Claude is unconfigured, rate-limited or returns
  nonsense, the session keeps its extractive recap and the job tries again later.

Needs `ADMIN_AI_ENABLED=true` and `ANTHROPIC_API_KEY`, plus **AI follow-up
enabled** in Live session settings.

## Background jobs

All registered in `apps/scheduler/jobs.py`; one cron entry ticking
`manage.py run_scheduled_jobs` drives them all.

| Job | Every | Does |
|---|---|---|
| `session-reminders` | 5 min | 24-hour and 30-minute reminders |
| `calendar-subscriptions` | 30 min | re-import connected Google / Outlook / Apple calendars |
| `session-pipeline` | 5 min | advance each finished session one step |
| `session-ai-followup` | 30 min | write the Claude session pack |

Unmatched attendees are not an error state — anonymous joining makes a few normal
every week. They wait on the session register for an educator, and the register
is correct for everyone that did match in the meantime.
| `sync-teams-meetings` | 15 min | the original recap/attendance sync |
| `finalise-attendance` | 15 min | close the register on ended sessions |

Each tick advances every pending session by **one** step and stops. Teams
publishes a recording anywhere between two minutes and several hours after a
call; YouTube quota can defer an upload to tomorrow; any step can fail on a
transient network error. Storing the state means a failure parks one session
while the other forty carry on, and the next tick resumes exactly where the last
one stopped.

By hand:

```bash
manage.py run_session_pipeline --session 42 --verbosity 2   # debug one session
manage.py send_session_reminders --dry-run                  # who would be told
manage.py run_session_ai_followup --session 42 --force
manage.py generate_session_thumbnails --all
```

## Extra Graph permissions

On top of what TEAMS_INTEGRATION.md lists, the pipeline needs (application
permissions, admin-consented):

- `Calendars.ReadWrite` — the Outlook invite for staff.
- `Files.ReadWrite.All` — building the folder tree and moving the recording.
- `Sites.ReadWrite.All` — only if recordings land in SharePoint rather than a
  personal OneDrive.

If your tenant blocks **anonymous** sharing links, `graph.create_share_link`
falls back to an organisation-scoped link automatically. That link will not play
for students, which is precisely the case YouTube covers.

## Where to look when something has not appeared

1. **Live session settings** page — connection badges for Teams and YouTube,
   remaining YouTube uploads today, and a count of sessions per pipeline state.
2. **Django admin → Session artifacts** — the state each session is stuck in and
   the last error Graph returned, with *Retry now* and *Start again* actions.
3. `manage.py run_scheduled_jobs --list` — last run, status and output per job.
4. The session's own page shows its processing state to admins and staff.
