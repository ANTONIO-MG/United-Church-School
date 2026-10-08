# Sign-in / sign-up artwork

Two photographs, one per auth page. Drop them in here with **exactly** these
names and nothing else needs changing:

| File | Page | Picture |
|---|---|---|
| `sign-in.jpg` | `/myhub/page-login/` | The learner in a live online session (headphones, video call on screen) |
| `sign-up.jpg` | `/myhub/page-register/` | The three learners working at their laptops |

Wired up in `templates/myhub/pages/page-login.html` and `page-register.html` via
the `{% block auth_image %}` in `templates/soft_ui/auth_base.html`.

Until a file is present the page falls back to the theme's own
`soft-ui/img/curved-images/curved6.jpg` — see the `static_or` tag in
`apps/communication/templatetags/org_branding.py` — so a missing photo shows the
stock background rather than a blank panel.

## Preparing the files

The panel is a tall, cropped strip on the right of the page (`background-size:
cover`), so the **subject should sit toward the middle-left** of the frame or it
will be cropped out on narrow screens. The photos supplied are 6000×4000; resize
before committing — a 6 MB background on the sign-in page is a slow first
impression:

```sh
# ~1400px wide is plenty for a half-page background on a retina screen
sips -Z 1400 sign-in.jpg
sips -Z 1400 sign-up.jpg
```

If you serve static files through `collectstatic`, run it after adding them.
