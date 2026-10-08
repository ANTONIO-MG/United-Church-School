# Google sign-in — setup guide

Everything needed to make the **Continue with Google** button work, in the
Google Cloud Console and in `.env`. Written to be repeatable: a new
organisation deploying this platform follows the same steps with their own
project and domain.

The app reads Google credentials from **environment variables only** — there is
no `SocialApp` row to create in the Django admin. If you have ever added one by
hand, delete it: with both a settings-based app and a DB row, allauth raises
`MultipleObjectsReturned`.

---

## 1. Create the OAuth client

1. Go to <https://console.cloud.google.com/> and create (or select) a project.
2. **APIs & Services → OAuth consent screen**
   - *User type*: **External** (unless everyone signing in has an account in
     your Google Workspace — then **Internal** and you can skip verification).
   - *App name*: what users see on the consent screen — use the public brand
     name, matching `brand.name` in `.strings.json`.
   - *User support email* and *Developer contact*: required; use a monitored
     address.
   - *App logo*: uploading one triggers Google **brand verification**, which can
     take days. Skip it for the first deploy if you need to launch.
   - *Authorised domains*: add your registered domain (e.g. `ucs.org.za`) —
     the bare domain, no scheme, no subdomain.
3. **Scopes**: add only `.../auth/userinfo.email` and `.../auth/userinfo.profile`.
   These are **non-sensitive** scopes, so no Google security review is needed.
   The app requests exactly these two (`SOCIALACCOUNT_PROVIDERS['google']['SCOPE']`
   in `config/settings.py`) — adding more, especially Gmail/Drive scopes, forces
   a review that takes weeks. Don't, unless a feature truly needs it.
4. **Credentials → Create credentials → OAuth client ID**
   - *Application type*: **Web application**.
   - *Authorised JavaScript origins* — the site origin, no path:
     ```
     https://your-domain.example
     http://127.0.0.1:8000          ← local development only
     ```
   - *Authorised redirect URIs* — **this exact path**, it is what allauth
     listens on. A trailing-slash or scheme mismatch is the single most common
     cause of `redirect_uri_mismatch`:
     ```
     https://your-domain.example/accounts/google/login/callback/
     http://127.0.0.1:8000/accounts/google/login/callback/     ← local dev only
     ```
     Add one line per environment you use (production, staging, local). Google
     matches these **literally** — `http` ≠ `https`, and `localhost` ≠ `127.0.0.1`.
5. Copy the **Client ID** and **Client secret**.

## 2. Publish the consent screen

**OAuth consent screen → Publishing status.**

While it says **Testing**, only accounts listed under *Test users* can sign in
(max 100), and refresh tokens expire after 7 days. Everyone else gets
*"has not completed the Google verification process"*. Press **Publish app**
before real users arrive.

With only the two non-sensitive scopes above, publishing is immediate — no
review. It's the *logo* and *sensitive scopes* that trigger verification.

## 3. `.env`

```ini
GOOGLE_OAUTH_CLIENT_ID=1077...-....apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=GOCSPX-...

# Must be the real public URL — it builds the links inside e-mails.
SITE_URL=https://your-domain.example
```

Leave **both** blank to hide/disable Google sign-in. Setting only one is worse
than setting neither: allauth registers a provider with broken credentials and
the button fails at Google with an opaque error rather than degrading.

`GOOGLE_OAUTH_SECRET` is a credential — it belongs in `.env` (git-ignored),
never in `settings.py` or `.strings.json`.

## 4. What Google gives us, and what still gets asked

The `profile` + `email` scopes return: e-mail (already verified by Google),
first/last name, and profile-picture URL.

That is **not** enough to use the platform. A Google sign-up still lands in the
normal onboarding gate (`apps/accounts/middleware.py` → `OnboardingMiddleware`),
which collects role, course, contact details and so on at
`/community/register/`. So Google sign-in skips the password and the e-mail
round-trip, not registration.

Two consequences worth knowing:

- **E-mail verification is skipped for Google accounts**
  (`SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'`). That is deliberate and safe:
  Google has already verified the address. A password sign-up still must
  confirm by e-mail.
- **Terms & Conditions are not captured on the Google path.** The T&C tickbox
  lives on the password sign-up form, so `Person.terms_accepted_at` stays null
  for Google sign-ups. If consent must be provable for every account, add the
  checkbox to the onboarding step as well — see
  `apps/accounts/forms.py::UCSSignupForm` for how consent is recorded.

## 5. Security notes

- `SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT` is **False** (allauth's
  default), and should stay that way. If it were True, anyone who signed up with
  a password using someone else's address would have their account silently
  joined to that person's Google login — an account-takeover path.
- `SOCIALACCOUNT_LOGIN_ON_GET = True` means clicking the button goes straight to
  Google with no interstitial. Convenient, and safe for login, but it does mean
  a crafted link can start the flow; allauth's `state` parameter is what
  prevents that being useful to an attacker. PKCE is enabled
  (`OAUTH_PKCE_ENABLED: True`).
- Rotate the client secret from **Credentials → your client → Reset secret** if
  it is ever committed or shared. The old secret stops working immediately.

## 6. Troubleshooting

| Symptom | Cause |
|---|---|
| `redirect_uri_mismatch` | The redirect URI isn't registered **exactly** — check scheme, host, and the trailing slash on `/accounts/google/login/callback/` |
| "App has not completed verification" | Consent screen still in **Testing** — publish it, or add the address as a test user |
| `MultipleObjectsReturned: SocialApp` | A `SocialApp` row exists in the DB *and* credentials are in settings. Delete the DB row |
| `invalid_client` | Client ID / secret mismatch, or the secret was reset in the console and `.env` wasn't updated |
| Button 500s / does nothing | Only one of the two env vars is set |
| Signs in but bounces to `/community/register/` | Correct — that's the onboarding gate, not an error |
