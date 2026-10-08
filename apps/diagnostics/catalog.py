"""The error dictionary: every error this platform can report, by code.

A code looks like ``CERT-8001``. It carries two pieces of information before you
look anything up:

* the **prefix** says *which part of the system* failed (``CERT`` = certificates),
* the **number's thousands digit** says *what kind of failure it is* — see
  :data:`CAUSE_CLASSES`. ``8xxx`` is always rendering/storage, in every domain.

So ``CERT-8001`` reads as "certificates, rendering problem" before anyone opens
this file, and the ranges mean a developer can triage a log by eye.

Every entry answers four questions, because a code with no remedy is just a
number:

``title``   one line, what went wrong
``why``     the conditions that produce it
``fix``     what a **developer** should change or check
``action``  what the **user** in front of the screen should do

Nothing here imports Django models, so the catalog can be read by a management
command, a test, or a support engineer with a Python prompt and no database.
"""

from collections import namedtuple

# ---------------------------------------------------------------------------
# Domains — the prefix half of a code
# ---------------------------------------------------------------------------
PREFIXES = {
    'SYS':  'Platform, configuration and anything unclassified',
    'AUTH': 'Sign-in, sign-up, sessions, lockout, multi-factor',
    'USER': 'Profiles, onboarding, enrolment, members and invitations',
    'CHAT': 'Direct and group messaging',
    'MEET': 'Live calls, meeting rooms and attendance',
    'NOTF': 'Notifications and announcements',
    'FEED': 'The social activity feed',
    'MAIL': 'Outbound e-mail and the in-system mailbox',
    'LRN':  'Lessons, subjects and the course player',
    'ASMT': 'Assessments, questions, attempts and marking',
    'CERT': 'Certificates and their downloads',
    'RPRT': 'Grades, report cards and exports',
    'ANLT': 'Analytics and dashboards',
    'TASK': 'Assignable tasks',
    'SHOP': 'Store, cart and orders',
    'FIN':  'Invoices, payments and receipts',
    'FILE': 'Uploads, media storage and file serving',
    'INTG': 'Microsoft Teams / Graph integration',
    'AI':   'AI authoring and the assistant',
    'SCHD': 'Scheduled and background jobs',
    'HUB':  'Dashboard, calendar, events and CMS pages',
    'DESK': 'The staff desk: dashboards, jobs, moderation, grades, imports',
    'REV':  'Revision cards (spaced repetition)',
    'BKP':  'Database backups and restores',
}

# ---------------------------------------------------------------------------
# Cause classes — the number half of a code
# ---------------------------------------------------------------------------
CAUSE_CLASSES = {
    1: ('Input / validation', 'The request was malformed or incomplete. Almost always user-fixable.'),
    2: ('Permission / access', 'The caller is authenticated but not allowed to do this.'),
    3: ('Missing / not found', 'The thing being acted on does not exist, or no longer does.'),
    4: ('Conflict / business rule', 'The request is well-formed but the system’s rules forbid it now.'),
    5: ('External service', 'A third party (Teams, SMTP, a payment gateway, an LLM) failed or was unreachable.'),
    6: ('Data integrity', 'Stored data is inconsistent with what the code requires.'),
    7: ('Configuration', 'A setting, key or dependency is missing or wrong on this deployment.'),
    8: ('Rendering / storage', 'Producing or persisting a file, image or document failed.'),
    9: ('Unexpected', 'An unhandled failure. Treat every one of these as a bug to be classified.'),
}

SEVERITIES = ('info', 'warning', 'error', 'critical')

ErrorSpec = namedtuple('ErrorSpec', 'code title why fix action severity')

_RAW = []


def _e(code, title, why, fix, action, severity='error'):
    _RAW.append(ErrorSpec(code, title, why, fix, action, severity))


# ===========================================================================
# SYS — platform
# ===========================================================================
_e('SYS-9001', 'Unhandled server error',
   'An exception reached the top of the request without being caught or classified. '
   'The middleware caught it so the user saw an error page rather than a blank response.',
   'Open the event, read the traceback, then either fix the bug or catch it at '
   'its source with core.errors.capture() and a specific code so it stops '
   'arriving here unclassified.',
   'Quote the reference shown on the error page to support; the request was not completed.',
   severity='critical')
_e('SYS-9002', 'Unclassified handled error',
   'Code caught an exception and logged it, but did not tag it with a code, so it was '
   'auto-classified from its module and exception type.',
   'Add an explicit core.errors.report()/capture() code at the raising site so '
   'this arrives with a documented remedy instead of being guessed at.',
   'Retry. If it repeats, quote the reference to support.',
   severity='warning')
_e('SYS-7001', 'Required setting missing',
   'A setting the code depends on is empty or absent from the environment.',
   'Check the project .env against .env.example; the event context names the setting.',
   'Report to an administrator — this is a server configuration problem, not something you can fix.',
   severity='critical')
_e('SYS-7002', 'Optional dependency not installed',
   'A feature needing an optional package was used and the package is not present.',
   'pip install the package named in the event context, then restart the server.',
   'The feature is unavailable on this server; ask an administrator to enable it.',
   severity='warning')
_e('SYS-5001', 'Cache backend unreachable',
   'USE_REDIS is on but Redis did not answer. The request continued without a cache.',
   'Check the Redis host/port in .env and that the service is running, or set USE_REDIS=false.',
   'Nothing — pages may simply be slower than usual.',
   severity='warning')
_e('SYS-6001', 'Database integrity violation',
   'A write broke a unique, foreign-key or not-null constraint.',
   'Read the constraint named in the event context. Usually a missing '
   'get_or_create(), a race, or a ModelForm that does not validate what the '
   'database requires.',
   'Retry once. If it persists, report it — the same data may already exist.')

# ===========================================================================
# AUTH — sign-in and identity
# ===========================================================================
_e('AUTH-1001', 'Sign-up rejected',
   'The sign-up form failed validation: weak/mismatched password, malformed address, or '
   'the Terms box was not ticked.',
   'apps.accounts.forms.UCSSignupForm. Field errors render inline; nothing is created.',
   'Correct the highlighted fields and submit again.',
   severity='info')
_e('AUTH-1002', 'CAPTCHA answer rejected',
   'The math CAPTCHA answer was wrong, blank or expired (challenges last a few minutes).',
   'apps.accounts.forms.UCSSignupForm (captcha field) / django-simple-captcha. Confirm '
   "captcha.urls is included and the CaptchaStore table exists (run migrate).",
   'Solve the sum shown next to the box and resubmit; use the refresh icon for a new sum.',
   severity='info')
_e('AUTH-2001', 'Sign-in refused: e-mail not verified',
   'The credentials were right but the address has never been confirmed. A fresh '
   'confirmation link was sent instead of a session.',
   'apps.myhub.views.page_login. Check outbound mail is actually being delivered.',
   'Open the link in the e-mail just sent to you, then sign in again.',
   severity='info')
_e('AUTH-2002', 'Account locked after repeated failures',
   'django-axes locked this account/IP pair after AXES_FAILURE_LIMIT failed sign-ins.',
   'Clear it in the admin under Access attempts, or run `manage.py axes_reset_username <email>`. '
   'AXES_FAILURE_LIMIT is deliberately matched to allauth’s per-account budget.',
   'Wait for the cool-off to pass, or reset your password to regain access.',
   severity='warning')
_e('AUTH-2003', 'Second factor required',
   'MFA_REQUIRED_FOR_STAFF is on and this privileged account has no second factor yet.',
   'apps.accounts.middleware.MfaRequiredMiddleware. Set MFA_REQUIRED_FOR_STAFF=false to relax it.',
   'Set up an authenticator app at /accounts/2fa/ to continue.',
   severity='info')
_e('AUTH-2004', 'Session expired or not signed in',
   'A page requiring a session was requested without one.',
   'Expected for anonymous traffic. A spike suggests SESSION_COOKIE_AGE is too short or '
   'the session store is being cleared.',
   'Sign in again — your session has expired.',
   severity='info')
_e('AUTH-3001', 'Password-reset link invalid or used',
   'The reset key was already consumed, expired, or altered.',
   'The allauth reset flow in config.auth_urls. Links are single-use and expire.',
   'Request a fresh reset e-mail and use the newest link.',
   severity='info')
_e('AUTH-5001', 'Social login provider failed',
   'The Google/Facebook OAuth exchange did not complete.',
   'Check the SocialApp credentials in the admin and that the callback URL matches the '
   'provider console exactly.',
   'Try again, or sign in with your e-mail address and password instead.')

# ===========================================================================
# USER — profiles, enrolment, members
# ===========================================================================
_e('USER-1001', 'Profile form rejected',
   'A required profile field was missing or invalid.',
   'apps.accounts.forms. Field errors render inline.',
   'Fix the highlighted fields and save again.',
   severity='info')
_e('USER-1002', 'Registration selection incomplete',
   'Step 2 of registration was submitted without choosing a grade, or without ticking '
   'at least one subject to register for.',
   'apps.accounts.views.register_course — validates programme_id + module_ids before saving '
   'the choice to the session.',
   'Pick your grade, then tick at least one subject to continue.',
   severity='info')
_e('USER-2001', 'Not permitted to manage members',
   'A non-admin tried to reach a management page or action.',
   'apps.accounts.middleware.ManagementAccessMiddleware and the _ADMIN_ONLY_URL_NAMES set.',
   'Ask an administrator to make the change for you.',
   severity='info')
_e('USER-2003', 'Social sign-in provider is not configured',
   'Somebody reached a social-login URL for a provider that has no SocialApp registered '
   'against this Site — a deep link, an old bookmark, or a crawler. The buttons for it are '
   'already hidden.',
   'apps.accounts.middleware.SocialAppGuardMiddleware converts it to a redirect. To actually '
   'enable the provider, add a Social application in the Django admin and attach it to the Site.',
   'Sign in with your e-mail address and password instead.',
   severity='info')
_e('USER-2004', 'Archived account could not be restored',
   'An administrator asked to restore a purged account from the archive park and the '
   'rebuild failed — usually a missing or moved archive directory, or a model that has '
   'changed shape since the account was parked.',
   'apps.accounts.archiving.restore_archive. Check AccountArchive.archive_dir still exists '
   'on disk and holds content.json. The archive itself is never modified by a failed '
   'attempt, so it is safe to fix the cause and retry.',
   'Ask an administrator to check the archive backup for this account.',
   severity='error')
_e('USER-3001', 'Person profile missing for a user',
   'A User row exists with no Person. Every user should get one from a post-save signal.',
   'apps.accounts.signals.create_person_profile. Users made by a raw SQL insert or a fixture '
   'that disabled signals will be missing one — backfill them.',
   'Report it; an administrator needs to repair the account.')
_e('USER-3002', 'Grade or subjects missing at registration',
   'When confirming registration the chosen grade, or the subjects under it, no longer '
   'exist or were deactivated between step 2 and step 3.',
   'apps.accounts.views.register_review re-loads Programme + ProgrammeModule from the session '
   'ids; a deleted/deactivated row sends the user back to the picker.',
   'Choose your grade and subjects again.',
   severity='info')
_e('USER-4001', 'Enrolment refused',
   'The learner is already enrolled, the course is full or inactive, or the registration '
   'invoice is unpaid.',
   'apps.accounts.services.enrol_person \u2014 check seats, status and invoice.',
   'Check the course is still open and any registration invoice is settled.',
   severity='info')
_e('USER-4002', 'Invitation no longer valid',
   'The invite token was already accepted, withdrawn or has expired.',
   'apps.accounts.models.Invitation — check its status field.',
   'Ask whoever invited you to send a new invitation.',
   severity='info')
_e('USER-8001', 'Profile picture could not be stored',
   'The upload was rejected by the image library or the storage backend refused the write.',
   'Confirm Pillow can open the file and that MEDIA_ROOT is writable.',
   'Upload a standard JPEG or PNG under a few megabytes.')

# ===========================================================================
# CHAT
# ===========================================================================
_e('CHAT-2001', 'Not a member of this conversation',
   'Someone requested a chat group they do not belong to.',
   'apps.communication.views.chat_room / api._is_member.',
   'Open the conversation from your own list instead of a saved link.',
   severity='info')
_e('CHAT-2002', 'Direct message blocked pending connection',
   'Two students may only message once a connection request has been accepted.',
   'apps.communication.services.can_direct_message.',
   'Send a connection request and wait for them to accept.',
   severity='info')
_e('CHAT-2003', 'Sender is muted or suspended',
   'An active moderation penalty forbids this user from posting.',
   'apps.communication.services.active_silencing_penalty. Penalties are visible in the admin.',
   'You cannot send messages until the restriction ends. Contact an administrator to appeal.',
   severity='info')
_e('CHAT-2004', 'Cannot edit or delete someone else’s message',
   'An edit or delete was attempted on a message the caller did not send.',
   'apps.communication.api.MessageViewSet.perform_update / perform_destroy.',
   'You can only change your own messages.',
   severity='info')
_e('CHAT-1001', 'Message rejected',
   'The message had neither text nor an attachment, or a field failed validation.',
   'apps.communication.serializers.MessageSerializer.',
   'Type something or attach a file before sending.',
   severity='info')
_e('CHAT-3001', 'Replied-to message no longer exists',
   'The parent message was deleted between opening the thread and sending the reply.',
   'Message.reply_to is SET_NULL, so the reply survives without its quote.',
   'Your reply was sent, but the message it quoted has been removed.',
   severity='info')
_e('CHAT-8001', 'Chat attachment could not be stored',
   'Saving an uploaded file to the media backend failed.',
   'Check FILES_ROOT/MEDIA_ROOT permissions and free space; see apps.communication.models.'
   'MessageAttachment.save.',
   'Try a smaller file, or send it again in a moment.')
_e('CHAT-6001', 'Conversation has no other members',
   'A direct chat was found with fewer than two memberships, so it cannot be titled or delivered.',
   'apps.communication.services.other_member returned None. Usually a deleted account; '
   'deactivate conversations when their last peer is removed.',
   'Start a new conversation with the person instead.',
   severity='warning')

# ===========================================================================
# MEET — calls and attendance
# ===========================================================================
_e('MEET-3001', 'Meeting room not found',
   'The slug in the link does not match any meeting, or the meeting was deleted.',
   'apps.communication.views.meeting_room resolves MeetingRoom by slug.',
   'Ask the host to resend the invitation link.',
   severity='info')
_e('MEET-4001', 'Class session is closed',
   'A presence heartbeat or check-in arrived for a session that is no longer open.',
   'apps.communication.views.attendance_ping returns 409 by design.',
   'The register for this session has been closed; speak to your educator.',
   severity='info')
_e('MEET-5001', 'Live meeting provider unreachable',
   'Creating or fetching the meeting failed at the provider.',
   'Jitsi: check JITSI_BASE_URL. Teams: see the INTG codes — the platform falls back to Jitsi '
   'when Graph is unavailable.',
   'Try starting the call again; if it keeps failing, use the meetings page.')
_e('MEET-8001', 'Attendance record could not be written',
   'Recording presence or finalising the register failed mid-write.',
   'apps.communication.services.record_presence_ping / finalise_session_attendance.',
   'Your attendance may not have been counted — tell your educator.')

# ===========================================================================
# NOTF — notifications and announcements
# ===========================================================================
_e('NOTF-2001', 'Notification belongs to someone else',
   'A notification was requested by a user who is not its recipient.',
   'apps.communication.views.notification_detail filters on recipient and 404s otherwise — '
   'deliberately a 404, not a 403, so it does not confirm the notification exists.',
   'Open notifications from your own inbox.',
   severity='info')
_e('NOTF-1001', 'Announcement rejected',
   'The announcement form was incomplete, or the audience resolved to nobody.',
   'apps.communication.forms.AnnouncementForm and services.send_announcement.',
   'Pick at least one recipient, course or subject and try again.',
   severity='info')
_e('NOTF-5001', 'Announcement e-mail delivery failed',
   'Notifications were created in-app but the e-mail leg failed for one or more recipients.',
   'Check the EMAIL_* settings and the provider’s logs — see the MAIL codes.',
   'Recipients can still see the announcement in the app.',
   severity='warning')

# ===========================================================================
# FEED
# ===========================================================================
_e('FEED-9001', 'A feed source failed and was skipped',
   'One contributor to the activity feed raised, so the feed rendered without it rather '
   'than failing the whole page.',
   'apps.communication.feed.build_feed isolates each source. The context names which one — '
   'fix that source; a silently short feed reads as "no activity" and goes unreported.',
   'Some recent activity may be missing; refresh in a moment.',
   severity='warning')
_e('FEED-1001', 'Post rejected',
   'The composer was submitted with no text and no attachment.',
   'apps.communication.views.feed_create requires body or media.',
   'Write something or attach a photo, video or file before posting.',
   severity='info')
_e('FEED-1002', 'Comment rejected',
   'A comment was submitted with no text once whitespace was stripped.',
   'apps.communication.views.feed_comment returns 400.',
   'Type a comment before sending.',
   severity='info')
_e('FEED-3001', 'Post no longer exists',
   'A like or comment arrived for a post that had been deleted.',
   'apps.communication.views.feed_like / feed_comment.',
   'Refresh the page — the post has been removed.',
   severity='info')

# ===========================================================================
# MAIL
# ===========================================================================
_e('MAIL-5001', 'Outbound e-mail failed',
   'The SMTP server or e-mail API rejected or could not be reached.',
   'Check EMAIL_HOST/PORT/USER/PASSWORD and TLS settings, and the provider’s sending limits. '
   'apps.communication.emails.send_branded_email.',
   'The message was not delivered. Try again, or contact the person another way.')
_e('MAIL-2001', 'Mailbox not available to this role',
   'The in-system mailbox is limited to staff and educators.',
   'apps.communication.views._can_use_mail gates on is_admin_staff / is_educator.',
   'Use chat instead — the mailbox is for staff and educators.',
   severity='info')
_e('MAIL-1001', 'Message rejected',
   'A module or at least one recipient was missing.',
   'apps.communication.views.mail_compose needs a module and a recipient.',
   'Add a subject and at least one recipient.',
   severity='info')
_e('MAIL-7001', 'E-mail template missing or broken',
   'A branded e-mail template failed to render.',
   'templates/communication/email/. A missing context key raises at render time.',
   'Report it — the notification could not be sent.')

# ===========================================================================
# LRN — lessons and courses
# ===========================================================================
_e('LRN-2001', 'Lesson not available to this learner',
   'The lesson is unpublished, outside its publish window, or targeted at a different '
   'module, class, role or individual.',
   'apps.learning.views._can_view_lesson — check status, publish_at/expire_at, visibility '
   'and target_* relations.',
   'It may not be published yet. Check with your educator.',
   severity='info')
_e('LRN-2002', 'Not permitted to author lessons',
   'A learner reached an authoring or editing route.',
   'apps.learning.authoring guards on _is_staff_like.',
   'Lesson authoring is for teachers and staff.',
   severity='info')
_e('LRN-2003', 'Subject locked — payment required',
   'A learner opened content that lives under a priced ProgrammeModule they have not paid '
   'for and are not trialling. They were redirected to the subject unlock page.',
   'apps.learning.views._locked_module_for_lesson / module_unlock — a module unlocks on a '
   '7-day trial or when its per-month invoice is paid (ModuleEnrolment.is_unlocked).',
   'Unlock the subject with a card payment (PayFast) or start the free trial to continue.',
   severity='info')
_e('LRN-1001', 'Lesson could not be saved',
   'A required field was missing — most often the subject.',
   'apps.learning.authoring.lesson_create / lesson_meta_save.',
   'Choose a subject and give the lesson a title.',
   severity='info')
_e('LRN-3001', 'Lesson, section or block not found',
   'The referenced content was deleted or belongs to a different lesson.',
   'apps.learning.authoring section/block handlers.',
   'Reload the editor — the item has been removed.',
   severity='info')
_e('LRN-3002', 'Subject not found',
   'A subject open/unlock route referenced a ProgrammeModule that does not exist or is inactive.',
   'apps.learning.views.module_unlock / my_modules — the offering was deleted or deactivated '
   'in the admin.',
   'Reload your subjects list — that subject is no longer available.',
   severity='info')
_e('LRN-4001', 'No subject exists to attach a lesson to',
   'Lesson authoring was opened before any subject had been created.',
   'apps.learning.models.Lesson requires a ProgrammeModule — the FK is not nullable.',
   'Create a subject first, then add lessons to it.',
   severity='info')
_e('LRN-8001', 'Lesson export failed',
   'Packaging a lesson or subject for download did not complete.',
   'Check the export/render helpers in apps.reports.certificates and the file paths they write to.',
   'Try the export again; if it keeps failing, report it.')

# ===========================================================================
# ASMT — assessments
# ===========================================================================
_e('ASMT-4001', 'Illegal assessment state change',
   'A transition was requested that the lifecycle does not allow — for example Draft '
   'straight to Open.',
   'apps.assessments.models.Assessment.STATUS_TRANSITIONS is the single source of truth; '
   'the builder only offers available_transitions().',
   'Move it through Review first — the builder shows the moves that are allowed.',
   severity='info')
_e('ASMT-4002', 'Cannot open an assessment with no questions',
   'Opening or scheduling was refused because the paper is empty.',
   'See Assessment.transition_to in apps.assessments.models — a paper needs at least one question before it can open.',
   'Add at least one question before opening it to learners.',
   severity='info')
_e('ASMT-4003', 'Assessment is not open',
   'A learner tried to start an assessment that is closed, draft, or outside its window.',
   'apps.assessments.views.take and _within_window.',
   'Check the opening times with your educator.',
   severity='info')
_e('ASMT-4004', 'No attempts remaining',
   'The learner has used every permitted attempt.',
   'Assessment.attempts_allowed versus their AssessmentAttempt count.',
   'Ask your educator whether another attempt can be granted.',
   severity='info')
_e('ASMT-2001', 'Not permitted to manage this assessment',
   'The caller does not teach the module the assessment belongs to.',
   'apps.assessments.authoring._can_manage / _managed_modules.',
   'Only teachers of this subject can build or mark it.',
   severity='info')
_e('ASMT-1001', 'Question could not be saved',
   'The question type, marks or options were missing or inconsistent.',
   'apps.assessments.authoring.question_save.',
   'Complete the question text, marks and at least one correct option.',
   severity='info')
_e('ASMT-6001', 'Attempt could not be marked',
   'Grading raised — usually an answer whose shape does not match its question type.',
   'apps.assessments.marking.grade_attempt. The event context names the question.',
   'Tell your educator the attempt could not be marked automatically.')
_e('ASMT-4005', 'Attempt ended by proctoring',
   'The integrity guard ended the attempt after too many focus losses.',
   'apps.assessments.proctoring — the Assessment.proctor_* fields set the limit '
   'and the action taken.',
   'Your attempt was submitted automatically. Speak to your educator if this was a mistake.',
   severity='warning')

# ===========================================================================
# CERT — certificates
# ===========================================================================
_e('CERT-1001', 'Certificate data is incomplete',
   'The certificate could not be described truthfully — no holder name, nothing named as '
   'achieved, or a malformed certificate number.',
   'apps.reports.certificates.render_data validates before drawing, deliberately raising '
   'rather than issuing a sheet with a blank name. The message names the field.',
   'The recipient’s profile is probably missing their name. Complete it and reissue.',
   severity='warning')
_e('CERT-2001', 'Not permitted to view this certificate',
   'Certificates are visible to their holder and to staff, educators and admins.',
   'apps.reports.views._certificate_for raises 404 rather than 403 so it does not confirm '
   'the certificate exists.',
   'Open it from your own Reports page.',
   severity='info')
_e('CERT-8001', 'Certificate artwork could not be rendered',
   'Drawing the certificate image failed part-way through render_image().',
   'apps.reports.certificate_render. Most likely the bundled fonts under '
   'static/fonts/certificate/ are missing — fonts_available() reports this.',
   'Try again shortly; if it persists, report it to an administrator.')
_e('CERT-8002', 'Certificate PDF could not be stored',
   'The rendered PDF could not be written to media storage.',
   'Check MEDIA_ROOT permissions and free space. A missing stored file is re-rendered '
   'automatically; a failed write is not.',
   'The download may still work — try it again.')
_e('CERT-7001', 'Certificate fonts missing',
   'One or more bundled fonts are absent, so the certificate renders in a fallback face.',
   'Restore static/fonts/certificate/ (Poppins + Great Vibes, both SIL OFL). '
   'certificate_render.fonts_available() is the check.',
   'The certificate will look wrong — tell an administrator before issuing it.',
   severity='warning')

# ===========================================================================
# RPRT — grades, report cards, exports
# ===========================================================================
_e('RPRT-6001', 'Grade could not be computed',
   'Recomputing a module grade failed — usually a weighting that does not total 100, or '
   'an assessment with no marks.',
   'apps.reports.services and ModuleWeighting.clean.',
   'Ask a teacher to check the subject’s weightings.')
_e('RPRT-7001', 'Excel export unavailable',
   'An .xlsx export was requested but openpyxl is not installed.',
   'pip install openpyxl and restart. apps.analytics.services.export_rows_xlsx.',
   'Export as CSV instead, or ask an administrator to enable Excel export.',
   severity='warning')
_e('RPRT-1001', 'Import file rejected',
   'A bulk import could not be read: wrong format, missing an "email" column, or a row '
   'with no address.',
   'apps.accounts.resources.PersonResource keys on e-mail. Grades are export-only by design.',
   'Export the template first, fill it in, and re-upload as .xlsx or .csv.',
   severity='info')

# ===========================================================================
# ANLT
# ===========================================================================
_e('ANLT-2001', 'Analytics restricted',
   'Analytics is limited to staff, admins and educators.',
   'apps.analytics.views guards on is_admin_staff / is_educator in core.roles.',
   'Ask an administrator if you need these figures.',
   severity='info')
_e('ANLT-9001', 'A dashboard panel failed to build',
   'One aggregation raised, so the panel rendered empty rather than failing the page.',
   'apps.analytics.services — the context names the panel. Check for division by '
   'zero on an empty class.',
   'Some figures may be missing; refresh in a moment.',
   severity='warning')

# ===========================================================================
# TASK
# ===========================================================================
_e('TASK-1001', 'Task could not be saved',
   'A required field was missing, or the assignment target did not resolve to anybody.',
   'apps.tasks.models.Task.assign_to and its fan-out.',
   'Choose who the task is for and give it a title and due date.',
   severity='info')
_e('TASK-2001', 'Not permitted to manage this task',
   'Only the creator, staff or admins may edit or delete a task.',
   'apps.tasks.views guards on the creator, staff or admin.',
   'Ask the person who set the task, or an administrator.',
   severity='info')
_e('TASK-3001', 'Task or assignment not found',
   'The task was deleted, or the assignment does not belong to this user.',
   'apps.tasks.views \u2014 the Task or its TaskAssignment no longer exists.',
   'Refresh your task list.',
   severity='info')

# ===========================================================================
# SHOP / FIN
# ===========================================================================
_e('SHOP-1001', 'Cart or order rejected',
   'The checkout had no course and no products, or a quantity was invalid.',
   'apps.shop.views checkout guards require a Course or at least one product.',
   'Add a course or at least one product before checking out.',
   severity='info')
_e('SHOP-3001', 'Order not found',
   'The order does not exist, or belongs to another customer.',
   'apps.shop.views scopes every order to its owner; staff see all of them.',
   'Open the order from your own orders list.',
   severity='info')
_e('SHOP-2001', 'Not permitted to view this order',
   'Orders are visible to their owner and to staff.',
   'apps.shop.views scopes every order to its owner; staff see all of them.',
   'Sign in as the account that placed the order.',
   severity='info')
_e('FIN-2001', 'Not permitted to view this invoice or receipt',
   'Finance documents are visible to their payer, the student’s parent, and staff.',
   'apps.finance.views guards: payer, the student\u2019s parent, or staff.',
   'Sign in as the account the invoice was issued to.',
   severity='info')
_e('FIN-5001', 'Payment gateway error',
   'PayFast rejected the redirect signature, or the ITN callback could not be verified.',
   'Check PAYFAST_* in .env and that the merchant ID/key match the environment (sandbox vs '
   'live). Never trust an unverified ITN.',
   'Your payment was not taken. Try again, or use another method.',
   severity='critical')
_e('FIN-6001', 'Payment recorded but reconciliation failed',
   'Money was taken but the invoice, enrolment or receipt did not update.',
   'Reconcile by hand from the PAYFAST reference in the event context against '
   'apps.finance.models.Payment. This needs a human — do not simply retry it.',
   'Your payment went through. Contact the office with your reference so it can be applied.',
   severity='critical')
_e('FIN-6002', 'Subject unlock after payment failed',
   'A subject invoice settled (PayFast or a manual mark) but activating the ModuleEnrolment(s) '
   'it was raised for did not complete, so the learner paid but the subject stayed locked.',
   'apps.accounts.signals.enrol_on_invoice_paid → apps.learning.enrolment.activate_modules_'
   'for_invoice. Re-run it for the invoice, or flip the ModuleEnrolment to active by hand from '
   'the invoice_uid. Do not re-charge.',
   'Your payment went through. Contact the office with your reference and the subject will be opened.',
   severity='critical')
_e('FIN-6003', 'Payment did not cover the invoice',
   'A verified PayFast ITN settled less than the invoice balance. The money is real and has '
   'been recorded, but the invoice stays partial — a genuine short payment, a currency/rounding '
   'mismatch, or a replayed notification for an older, smaller balance.',
   'apps.finance.views.payfast_notify compares amount_gross against Invoice.balance before '
   'settling. Reconcile the difference by hand from the PayFast reference; do not close the '
   'invoice without it. Never widen the tolerance to make this go away.',
   'Part of your payment was received. Contact the office with your reference to settle the '
   'balance.',
   severity='critical')
_e('FIN-8001', 'Invoice or receipt PDF failed',
   'Rendering the finance PDF did not complete.',
   'apps.finance.pdf uses xhtml2pdf, which supports only a narrow CSS subset — percentage '
   'heights and flexbox will break it.',
   'The document is still viewable on screen; try the download again later.')
_e('FIN-8002', 'Subject invoice could not be raised',
   'Creating the per-subject invoice (registration or a single-subject unlock) failed while '
   'writing the Invoice / InvoiceItem rows.',
   'apps.learning.enrolment.invoice_for_modules / unlock_single_module, called from '
   'apps.accounts.views.register_review and apps.learning.views.module_unlock. Check the '
   'finance models and the DB write.',
   'We could not raise your invoice. Try again, or contact the office.')

# ===========================================================================
# FILE
# ===========================================================================
_e('FILE-8001', 'Upload could not be stored',
   'The configured storage backend refused to write the uploaded file.',
   'Check FILES_ROOT/MEDIA_ROOT permissions, free space, and the S3/Azure credentials if a '
   'remote backend is configured.',
   'Try uploading again; if it keeps failing, report it.')
_e('FILE-1001', 'File type or size rejected',
   'The upload is not an accepted type, or exceeds the size limit.',
   'The accepted extensions are listed on each model — e.g. MessageAttachment.IMAGE_EXTS.',
   'Convert the file to an accepted format, or upload a smaller one.',
   severity='info')
_e('FILE-3001', 'Stored file is missing',
   'A database row references a file that is no longer in storage.',
   'Check MEDIA_ROOT / FILES_ROOT in config.settings — usually a wiped media folder, or a '
   'storage backend switched without migrating the files across. Certificates re-render '
   'themselves; most other uploads cannot.',
   'The file is no longer available — ask whoever uploaded it to send it again.',
   severity='warning')

# ===========================================================================
# INTG — Microsoft Teams / Graph
# ===========================================================================
_e('INTG-7001', 'Teams integration not configured',
   'A Teams action was attempted with MS_GRAPH_* unset. The platform fell back to Jitsi.',
   'Set MS_GRAPH_TENANT_ID / CLIENT_ID / CLIENT_SECRET — see docs/TEAMS_INTEGRATION.md. '
   'Dormant is a supported state, not a fault.',
   'Your class will run on the built-in video instead of Teams.',
   severity='info')
_e('INTG-5001', 'Microsoft Graph request failed',
   'Graph returned an error or was unreachable when creating a meeting or syncing artifacts.',
   'Check the MS_GRAPH app registration’s permissions and that the client secret '
   'has not expired. The context carries the Graph error code.',
   'The class link may be missing — refresh, or ask your educator to recreate it.')
_e('INTG-5002', 'Teams token could not be acquired',
   'The client-credentials token request to Microsoft failed.',
   'A rotated or expired client secret is the usual cause. apps.msteams token helper.',
   'Live classes are temporarily unavailable; an administrator has been notified.',
   severity='critical')
_e('INTG-3001', 'Teams attendance report not available',
   'Graph had no attendance report for the meeting, usually because it has not ended yet.',
   'apps.msteams — Graph publishes attendance only after a meeting closes, and '
   'the sync retries on its next run.',
   'Attendance will appear once the class has finished.',
   severity='info')

# ===========================================================================
# ===========================================================================
# ===========================================================================
# AI
# ===========================================================================
_e('AI-7001', 'AI features not enabled',
   'An AI route was used with no provider configured.',
   'Set ANTHROPIC_API_KEY + ADMIN_AI_ENABLED, or AI_ASSISTANT_ENABLED and the AI_LLM_* '
   'settings. Dormant is a supported state.',
   'This feature is switched off on this server.',
   severity='info')
_e('AI-2001', 'AI assistant restricted',
   'The admin assistant is limited to admins and staff.',
   'apps.ai_assistant.views guards on role_flags()["is_admin_staff"].',
   'This assistant is for administrators and staff.',
   severity='info')
_e('AI-5001', 'AI provider request failed',
   'The model provider returned an error, refused the request, or timed out.',
   'Check AI_LLM_API_KEY / ANTHROPIC_API_KEY, the model name and your quota. Long '
   'documents can exceed the context window — apps.ai_assistant chunks them.',
   'Try again with a shorter document, or in a few minutes.')
_e('AI-1001', 'AI import needs a document or a description',
   'Generation was requested with neither an attachment nor a prompt.',
   'apps.learning.ai_import / apps.assessments.ai_import.',
   'Attach a document, describe what you want, or do both.',
   severity='info')
_e('AI-8001', 'Document text could not be extracted',
   'A PDF, .docx or .xlsx could not be read for AI import.',
   'apps.ai_assistant.docextract. Scanned PDFs have no text layer — they need OCR, which '
   'is not installed.',
   'Export the document as a text-based PDF or a Word file and try again.',
   severity='warning')

# ===========================================================================
# SCHD / HUB
# ===========================================================================
_e('SCHD-9001', 'Scheduled job failed',
   'A background job raised. Other jobs in the run continued.',
   'apps.scheduler.jobs. The context names the job; jobs must be idempotent so a rerun '
   'is always safe.',
   'Nothing — an administrator has been notified.',
   severity='warning')
_e('SCHD-5001', 'Scheduled job could not reach a dependency',
   'A job needed a service (mail, Graph, the database) that was unavailable.',
   'Check the dependency named in the context, then rerun via apps.scheduler.jobs.',
   'Nothing — it will be retried.',
   severity='warning')
_e('HUB-1001', 'Calendar entry rejected',
   'An event or reminder was saved without a title or a valid start date/time.',
   'apps.myhub.views event handlers validate through forms.EventForm.',
   'Give it a title and a valid date and time.',
   severity='info')
_e('HUB-3001', 'Page or record not found',
   'A dashboard, CMS page or record no longer exists.',
   'apps.myhub.views \u2014 the record was deleted or the URL is stale.',
   'Use the menu to navigate — the link you followed is out of date.',
   severity='info')
_e('HUB-2001', 'Section restricted to administrators',
   'School-management pages are admin/staff only.',
   'apps.accounts.middleware.ManagementAccessMiddleware.',
   'Ask an administrator if you need access.',
   severity='info')


#: Fallback used when nothing more specific is known.
UNKNOWN = 'SYS-9002'
UNHANDLED = 'SYS-9001'


def get(code):
    """The :class:`ErrorSpec` for ``code``, or the unclassified spec."""
    return ERRORS.get(code) or ERRORS[UNKNOWN]


def exists(code):
    return code in ERRORS


def prefix_of(code):
    return (code or '').split('-', 1)[0]


def cause_of(code):
    """The cause class (1–9) encoded in a code's number, or ``None``."""
    try:
        return int((code or '').split('-', 1)[1][0])
    except (IndexError, ValueError):
        return None


def cause_label(code):
    entry = CAUSE_CLASSES.get(cause_of(code))
    return entry[0] if entry else 'Unclassified'


def by_prefix():
    """``{prefix: [spec, …]}``, each list sorted by code — how the UI groups them."""
    grouped = {}
    for spec in sorted(ERRORS.values(), key=lambda s: s.code):
        grouped.setdefault(prefix_of(spec.code), []).append(spec)
    return grouped


def validate():
    """Return a list of problems with the catalog itself. Empty means healthy.

    Run by ``manage.py errorcheck`` and by the test suite, so a half-written
    entry can never ship: a code whose remedy is blank is no better than no code.
    """
    problems = []
    for code, spec in sorted(ERRORS.items()):
        if prefix_of(code) not in PREFIXES:
            problems.append(f'{code}: prefix "{prefix_of(code)}" is not a known domain')
        if cause_of(code) not in CAUSE_CLASSES:
            problems.append(f'{code}: number does not start with a known cause class 1–9')
        if spec.severity not in SEVERITIES:
            problems.append(f'{code}: severity "{spec.severity}" is not one of {SEVERITIES}')
        for field in ('title', 'why', 'fix', 'action'):
            if not (getattr(spec, field) or '').strip():
                problems.append(f'{code}: {field} is empty')
    return problems


# ===========================================================================
# NOTF — the broadcast composer and automatic notifications
# ===========================================================================
_e('NOTF-1002', 'Broadcast file rejected',
   'A file attached in the notification composer had a disallowed type, was over 100 MB, '
   'or took the notification past its 10-file limit.',
   'apps.communication.views._broadcast_files and core.validators.validate_broadcast.',
   'Remove that file (or shrink it) and send again.',
   severity='info')
_e('NOTF-4001', 'Broadcast action not allowed now',
   'Send / cancel / delete was asked of a notification in a state that does not allow it '
   '(e.g. deleting one that already went out).',
   'apps.communication.views.announcement_action — the buttons shown follow the status, so '
   'a spike usually means a stale page or a double click.',
   'Refresh the page; the notification has probably already moved on.',
   severity='info')
_e('NOTF-5002', 'Broadcast e-mail copy failed',
   'The in-app notification was delivered but the e-mail copy to one recipient failed.',
   'apps.communication.broadcast.send → emails.email_announcement_copy. Check EMAIL_* settings '
   'and the recipient address; see the MAIL codes for the provider side.',
   'Nothing: the notification is in their bell. Re-send by e-mail only if it was urgent.',
   severity='warning')
_e('NOTF-9002', 'Broadcast stopped part-way',
   'Sending a staff notification raised after some recipients were reached. The row is '
   'marked Failed with the reason; "Send now" resumes with only the people not yet reached.',
   'apps.communication.broadcast.send. The context has the announcement id; the traceback '
   'says which recipient or step failed.',
   'Open the notification in the Notifications centre and press "Send now" to resume.')
_e('NOTF-9003', 'Background broadcast thread crashed',
   'A large broadcast handed to a background thread died before it could record a result.',
   'apps.communication.broadcast.dispatch._run. Look for a restart during the send; the '
   'row may be stuck in "Sending" — set it to Failed and resume.',
   'Check the Notifications centre; resume the send if it shows Failed.')
_e('NOTF-9004', 'Automatic notification could not be queued',
   'A content change (material, lesson, assessment, task, video) was saved but queueing its '
   'notification raised. The save itself succeeded.',
   'apps.communication.auto_signals._later → the queue_* function named in the context.',
   'Nothing for the user. Staff can announce it by hand in the Notifications centre.',
   severity='warning')
_e('NOTF-9005', 'Automatic notification failed to send',
   'One queued automatic notification raised while being delivered; the rest of the run '
   'continued and this one stays queued for the next run.',
   'apps.communication.auto.run. The context has the AutoNotice key.',
   'Nothing — it is retried on the next run.',
   severity='warning')
_e('NOTF-9006', 'Weekly summary or re-engagement failed for a person',
   'Building one person\'s weekly summary or re-engagement nudge raised; everyone else was '
   'still sent theirs.',
   'apps.communication.weekly (student_lines / educator_lines). The context has the user id.',
   'Nothing — the next run tries again.',
   severity='warning')

# ===========================================================================
# DESK — the staff desk
# ===========================================================================
_e('DESK-2001', 'Staff desk refused',
   'Someone who is not admin or staff (or, for the teaching desk, not an educator) opened a '
   'staff-desk page.',
   'apps.staffdesk.access.staff_required / teaching_required.',
   'These pages are for the admin team. Ask an administrator if you need something from them.',
   severity='info')
_e('DESK-4001', 'Nudge already sent today',
   'An educator asked to nudge a module\'s inactive students within 24 hours of the last nudge.',
   'apps.staffdesk.dashboards — the rate limit protects students from repeat messages.',
   'Wait until the time shown on the button, then nudge again.',
   severity='info')
_e('DESK-9002', 'Manual job run crashed',
   '"Run now" on the Background jobs page started a job on a background thread and it '
   'raised outside the job runner\'s own error capture.',
   'apps.staffdesk.views_ops._background. Job-level failures are SCHD-9001; this one means the '
   'thread itself failed (e.g. the database went away).',
   'Try "Run now" again; if it repeats, check the Background jobs page and the error log.')
_e('DESK-9003', 'Content import failed',
   'A content import started from the staff desk raised. The run is marked Failed with its output.',
   'apps.staffdesk.views_academic._execute — the run history has the command, arguments and output.',
   'Open the run in Content imports, fix what the output says, and run it again.')
_e('DESK-9004', 'A dashboard panel failed',
   'One panel of a staff-desk dashboard raised and was shown empty so the rest of the page '
   'could load.',
   'apps.staffdesk.dashboards._panel — the context names the panel.',
   'The other panels are correct; refresh later.',
   severity='warning')

# ===========================================================================
# REV — revision cards
# ===========================================================================
_e('REV-9002', 'Revision cards could not be built',
   'An attempt was marked but turning its missed questions into revision cards raised. '
   'Marking itself succeeded.',
   'apps.revision.signals. Rebuild with `manage.py build_review_cards --user <id>`.',
   'Nothing — your marks are safe; cards will appear after the next rebuild.',
   severity='warning')

# ===========================================================================
# USER — names and the person card
# ===========================================================================
_e('USER-9002', 'Profile name could not be copied to the login',
   'Saving a profile tried to copy its first/last name onto the login account and failed. '
   'The profile saved; some pages may show the old name until the next save.',
   'apps.accounts.names.sync_login_name — check the database error in the traceback; the '
   'copy is a plain UPDATE of auth_user first_name/last_name.',
   'Save your profile again.',
   severity='warning')

# ===========================================================================
# SCHD — the runner itself
# ===========================================================================
_e('SCHD-7001', 'Background scheduler is not running',
   'No scheduled job has started for over 15 minutes during operating hours, so reminders, '
   'scheduled notifications and automatic notices are not going out.',
   'apps.scheduler (the timers in deploy/scheduler/production): check '
   '`systemctl list-timers \'ucs-lms-scheduler*\'` and `journalctl -u ucs-lms-scheduler`.',
   'Nothing for users; an administrator needs to restart the timers.',
   severity='critical')

# ===========================================================================
# BKP — database backups and restores
# ===========================================================================
_e('BKP-1001', 'Backup file rejected',
   'An uploaded or selected backup was not a PostgreSQL custom-format dump, or its name '
   'tried to point outside the backups folder.',
   'apps.staffdesk.backups.validate_dump (pg_restore --list must read it).',
   'Choose a backup made by this system (.dump).',
   severity='info')
_e('BKP-2001', 'Restore refused',
   'Someone who is not an administrator, or who did not type the confirmation, tried to '
   'restore the database.',
   'apps.staffdesk.views_backups — restores are admin-only and need the typed confirmation.',
   'Only an administrator can restore. Type the confirmation exactly as shown.',
   severity='warning')
_e('BKP-5001', 'Backup failed',
   'pg_dump exited with an error, so no new restore point was made.',
   'apps.staffdesk.backups.create_backup — the context has pg_dump\'s stderr. Check disk space, '
   'database credentials in .env and that pg_dump matches the server version.',
   'Try again; if it keeps failing, contact the developer. Existing backups are untouched.',
   severity='critical')
_e('BKP-5002', 'Restore failed',
   'pg_restore exited with an error. A safety backup was taken just before the restore '
   'started and is listed on the Backups page.',
   'apps.staffdesk.backups.restore_backup — the context has pg_restore\'s stderr.',
   'Restore the safety backup listed on the Backups page to return to where you were.',
   severity='critical')
_e('BKP-7001', 'Backup tools missing',
   'pg_dump / pg_restore could not be found on this server.',
   'Install postgresql-client matching the server version, or set PG_BIN_DIR.',
   'Contact the developer.',
   severity='critical')

# ===========================================================================
# Per-domain "unexpected" codes
# ===========================================================================
# Auto-classification needs a home in every domain: without these, an untagged
# failure in (say) finance whose cause class has no documented code would fall
# all the way back to SYS and lose the one thing we did know about it — which
# part of the platform it came from. Landing on FIN-9001 keeps that.
_e('DESK-9001', 'Unexpected DESK error',
   'An untagged failure in the DESK area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing DESK code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.')
_e('REV-9001', 'Unexpected REV error',
   'An untagged failure in the REV area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing REV code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.')
_e('BKP-9001', 'Unexpected BKP error',
   'An untagged failure in the BKP area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing BKP code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.')
_e('AUTH-9001', 'Unexpected AUTH error',
   'An untagged failure in the AUTH area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing AUTH code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('USER-9001', 'Unexpected USER error',
   'An untagged failure in the USER area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing USER code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('CHAT-9001', 'Unexpected CHAT error',
   'An untagged failure in the CHAT area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing CHAT code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('MEET-9001', 'Unexpected MEET error',
   'An untagged failure in the MEET area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing MEET code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('NOTF-9001', 'Unexpected NOTF error',
   'An untagged failure in the NOTF area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing NOTF code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('MAIL-9001', 'Unexpected MAIL error',
   'An untagged failure in the MAIL area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing MAIL code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('LRN-9001', 'Unexpected LRN error',
   'An untagged failure in the LRN area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing LRN code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('ASMT-9001', 'Unexpected ASMT error',
   'An untagged failure in the ASMT area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing ASMT code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('CERT-9001', 'Unexpected CERT error',
   'An untagged failure in the CERT area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing CERT code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('RPRT-9001', 'Unexpected RPRT error',
   'An untagged failure in the RPRT area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing RPRT code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('TASK-9001', 'Unexpected TASK error',
   'An untagged failure in the TASK area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing TASK code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('SHOP-9001', 'Unexpected SHOP error',
   'An untagged failure in the SHOP area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing SHOP code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('FIN-9001', 'Unexpected FIN error',
   'An untagged failure in the FIN area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing FIN code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('FILE-9001', 'Unexpected FILE error',
   'An untagged failure in the FILE area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing FILE code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('INTG-9001', 'Unexpected INTG error',
   'An untagged failure in the INTG area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing INTG code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('AI-9001', 'Unexpected AI error',
   'An untagged failure in the AI area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing AI code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')
_e('HUB-9001', 'Unexpected HUB error',
   'An untagged failure in the HUB area. It was classified from the module it came '
   'from, so the domain is right but the specific cause is not documented yet.',
   'Open the event, read the traceback, then tag the raising site with core.errors.capture() '
   'and either an existing HUB code or a new one in apps.diagnostics.catalog.',
   'Retry the action. If it repeats, quote the reference to support.',
   severity='warning')


# ---------------------------------------------------------------------------
# The dictionary itself — built last, so it sees every entry above.
# ---------------------------------------------------------------------------
ERRORS = {spec.code: spec for spec in _RAW}
