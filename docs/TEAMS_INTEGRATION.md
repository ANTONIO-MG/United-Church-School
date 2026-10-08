# Microsoft Teams live-classroom integration

> **See also [LIVE_SESSIONS.md](LIVE_SESSIONS.md)** — the layer built on top of
> this one: the school calendar, audience scoping, per-recipient time zones, the
> 24h/30m reminders, and the pipeline that files each recording into OneDrive,
> publishes it as a past session, uploads it to YouTube and writes the follow-up
> pack. This document stays the reference for the Graph auth model itself.

Replaces the embedded Jitsi meetings with **Microsoft Teams**, driven entirely
from the LMS through the **Microsoft Graph API**. Educators never open Teams;
students/parents join anonymously from a link inside the LMS.

```
                     Django LMS  (system of record)
   Courses · Lessons · Assessments · Calendar · Files · Attendance · Feedback
                          │
      ┌───────────────────┼────────────────────┐
 Course mgmt         Student portal        Live sessions
      │                   │                    │
      └──────────────► Microsoft Graph ◄───────┘   (app-only / client credentials)
                             │
                     Microsoft Teams                 (live A/V engine only)
        ┌────────────────────┴───────────────────┐
   Licensed staff                            Students / parents
   (educators/admins host)                   (anonymous, join by link)
```

## What runs where

| Concern | Owner |
|---|---|
| Create / schedule a meeting, assign the organizer, get the join link | **LMS → Graph** (`POST /users/{organizer}/onlineMeetings`) |
| Host controls: screen share, whiteboard, breakout rooms, recording, polls, chat, files | **Teams** (in the live call) |
| Recording, transcript, attendance report | **Graph** pulls them back into the LMS |
| Summary / notes / action items / decisions / questions / timeline | **LMS** generates them *from the transcript* (see "Recap") |
| Everything a student sees: upcoming sessions, join button, recording, recap, attendance | **LMS** |

## Auth model — app-only (client credentials)

So the LMS can create meetings for an educator **without that educator signing
in**, we use **application permissions** (not delegated):

- Register an app in **Entra ID (Azure AD)** → client id + client secret + tenant id.
- Grant **application** Graph permissions (admin consent):
  `OnlineMeetings.ReadWrite.All`, `OnlineMeetingTranscript.Read.All`,
  `OnlineMeetingRecording.Read.All`, `OnlineMeetingArtifact.Read.All`,
  `User.Read.All`, and — for the live-session pipeline —
  `Calendars.ReadWrite` (the staff Outlook invite) and `Files.ReadWrite.All`
  (building the OneDrive folder tree and moving the recording into it). Add
  `Sites.ReadWrite.All` only if recordings land in SharePoint rather than a
  personal OneDrive.
- **One-time Teams admin step (required):** an *application access policy* lets the
  app act on behalf of your licensed educators. In Teams PowerShell:
  ```powershell
  New-CsApplicationAccessPolicy -Identity LMS-Meetings `
      -AppIds "<CLIENT_ID>" -Description "LMS creates Teams meetings"
  # grant to the licensed educators (or -Global for all):
  Grant-CsApplicationAccessPolicy -PolicyName LMS-Meetings -Identity educator@yourschool.com
  ```
  Without this policy Graph returns 403 on meeting creation.

## Licensing (important correction)

Microsoft licenses are **per user, not per subject**. The "one license per
subject/course" rule works like this: each subject has a **hosting educator**
whose licensed account (Teams Essentials / M365 Business / A1-A3) is the meeting
**organizer**; the LMS creates that subject's meetings on their behalf and
auto-links them to the subject. **Students and parents need no license** — they
join anonymously via the `joinWebUrl`.

## Join model — anonymous

Students/parents click the Teams **join link** embedded in the LMS. No Microsoft
account, no sign-in. Teams meetings can't be `<iframe>`-embedded (Teams blocks
it), so the LMS "meeting room" page is a **launch page**: session details, a
"Join the Teams class" button, and — afterwards — the recording, transcript,
recap and attendance, so students rarely leave the LMS.

## Recap — generated from the transcript

**Graph does not expose Copilot's meeting recap.** It *does* expose the
transcript, the recording, and the attendance report. So the LMS generates the
recap itself from the transcript:

- **Automatic (every class):** a fast extractive/template summary — key points,
  action items, decisions, questions, a rough timeline — no external cost.
- **Admin-triggered (richer):** the existing Claude admin layer
  (`apps.ai_assistant.admin_ai`) rewrites the transcript into a polished recap.

The recap is stored as an `AiReport` (kind `meeting_recap`), filed to the
subject/course documents, posted to the class feed, and the attendance report is
reconciled into the existing `Attendance` rows.

## After-class pipeline

1. Meeting ends → `sync_teams_meetings` (management command, cron/Celery) polls
   Graph for meetings whose `scheduled_end` has passed and that aren't synced.
2. Fetch transcript (`/onlineMeetings/{id}/transcripts`), recording
   (`/recordings`), attendance (`/attendanceReports`).
3. Generate recap from the transcript; file artifacts to the subject.
4. Reconcile attendance; post recap + recording to the class feed / lesson.

## Config (`.env`)

```
MEETING_PROVIDER=teams            # teams | jitsi  (jitsi kept as fallback)
MS_TEAMS_ENABLED=true
MS_GRAPH_TENANT_ID=<tenant-guid>
MS_GRAPH_CLIENT_ID=<app-client-id>
MS_GRAPH_CLIENT_SECRET=<app-secret>     # store securely; rotate regularly
MS_GRAPH_DEFAULT_ORGANIZER=principal@yourschool.com   # fallback organizer UPN
```

Until these are set the integration is **dormant**: meeting creation falls back
to the in-app page and nothing breaks.

## Mapping educators → organizer

The meeting organizer is the educator's **Microsoft UPN** (usually their work
e-mail). By default the LMS uses the educator's account e-mail; a per-user
override can be stored on their profile if the Microsoft UPN differs.

## Replaces / retires

- Jitsi embed (`meet.jit.si`, `JITSI_BASE_URL`) → Teams (Jitsi kept as fallback
  only when `MEETING_PROVIDER=jitsi`).
- The CrewAI + Ollama assistant runtime (resource-heavy) is retired; the
  `AiReport`/`AiInsight` tables are repurposed to store Teams recaps. The Claude
  **admin** layer stays for admin users.
