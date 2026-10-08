# Real-time / WebSockets (Django Channels)

The UCS LMS uses [Django Channels](https://channels.readthedocs.io/) to push events to
the browser over WebSockets, so the UI reacts the instant something happens
instead of waiting for the next poll. **Polling is kept as an automatic
fallback** — if no ASGI server is running, or a socket drops, or
`WEBSOCKETS_ENABLED=false`, everything still works over the existing REST endpoints.

## What is real-time today

| Feature | Socket | What it does |
|---|---|---|
| **Notification & message alerts** | `ws/alerts/` (per user) | The moment a notification or a message addressed to you is created, the navbar bell chimes (`window.appSound`) and shows its unread dot — no 20-second poll delay. |
| **Chat delivery** | `ws/chat/<group_id>/` (per conversation) | When anyone posts to a conversation, every open messenger for it refreshes immediately instead of on its 5-second timer. |
| **Live lesson presence + hand-raising** | `ws/lesson/<lesson_id>/` (per lesson) | The lesson rail shows a live "N here now" roster of everyone currently viewing the lesson, and a **raise/lower-hand** toggle every viewer sees (raised avatars are ringed; a "N hands up: …" line lists who). |

**Live lesson presence — how the roster stays correct without a server-side
store.** Presence is *peer-announced* over the channel layer, so it works with
the Redis layer across workers and needs no shared roster: on connect a client
broadcasts a `join` with its identity; every already-present client answers with
a `sync` of *its* identity (so the newcomer learns who is here); on disconnect a
`leave` is broadcast. A `sync` never triggers another `sync`, so it cannot loop.
The browser holds the roster and renders the avatars. Access is gated by the same
`_can_view_lesson` rule the lesson page uses. The live classroom *video* itself
stays on Microsoft Teams (see [TEAMS_INTEGRATION.md](TEAMS_INTEGRATION.md)) —
Channels handles the LMS-side presence around it.

**Hand-raising** rides the same consumer: the client sends `{"action":"hand",
"up":true|false}`, the consumer stores it on that user's presence record and
broadcasts a `presence_hand` event; each client's roster carries a `hand` flag
(so it is included in the join/sync a newcomer receives, and existing raised
hands show immediately). On connect the consumer also sends the client a `self`
event with its own identity, so the browser knows which roster entry is "me" to
toggle. A synced section timer or live reactions would extend it the same way —
a new client action, a new broadcast event handler.

## How it fits together

```
Browser  ──ws://…/ws/alerts/──►  AlertConsumer   ┐
Browser  ──ws://…/ws/chat/12/─►  ChatConsumer    ├─ channel layer ─┐
                                                  ┘   (Redis / mem) │
Django view / DRF / notify() ──── realtime.push_* ──────────────────┘
```

- **`config/asgi.py`** — the ASGI entry point. A `ProtocolTypeRouter` sends HTTP
  to Django and `ws://` to the WebSocket router, wrapped in
  `AllowedHostsOriginValidator` (same-origin only) + `AuthMiddlewareStack` (so
  `scope['user']` is the logged-in user in every consumer).
- **`apps/communication/routing.py`** — the `ws/…` URL patterns.
- **`apps/communication/consumers.py`** — `AlertConsumer` (per-user group
  `alerts_<id>`), `ChatConsumer` (per-conversation group `chat_<id>`, membership
  checked on connect) and `LessonPresenceConsumer` (per-lesson group
  `lesson_<id>`, access checked via `_can_view_lesson`).
- **`apps/communication/realtime.py`** — server-side senders (`push_alert`,
  `push_chat`, `broadcast_new_message`). All best-effort: they never raise, so a
  failed push can't break a message send or a notification.
- **Producers** — `notify()` (`services.py`) pushes a notification alert;
  `MessageViewSet.perform_create` (`api.py`) calls `broadcast_new_message`.
- **Clients** — `static/js/chrome.js` (the alert socket, with the counts poller
  as fallback) and `templates/communication/_chat_script.html` (the chat socket,
  with the 5-second poll as fallback).

## Configuration

Settings live in `config/settings.py`; values come from the environment.

| Env var | Default | Meaning |
|---|---|---|
| `WEBSOCKETS_ENABLED` | `true` | Master switch surfaced to the app. Off ⇒ rely on polling. |
| `USE_REDIS` | `false` | Also selects the **channel layer**: `true` ⇒ Redis, `false` ⇒ in-memory. |
| `CHANNEL_REDIS_URL` | `redis://127.0.0.1:6379/2` | Redis for the channel layer (own db, separate from the cache's db 1). Used only when `USE_REDIS=true`. |

**The channel layer choice matters:**

- **In-memory** (`InMemoryChannelLayer`, the default when `USE_REDIS=false`) is
  fine for a **single-process** dev server. It is **not shared across processes**,
  so with more than one worker a push on worker A never reaches a socket on
  worker B.
- **Redis** (`channels_redis`) is **required in production** and any time you run
  more than one process (gunicorn workers, multiple daphne instances, etc.). Set
  `USE_REDIS=true` and point `CHANNEL_REDIS_URL` at your Redis.

## Running

`daphne` is listed **first** in `INSTALLED_APPS`, so Django's `runserver` is
replaced by the Channels ASGI dev server automatically — WebSockets work in
development with no extra command:

```bash
python manage.py runserver
```

**Production** runs the ASGI app (`config.asgi:application`) under an ASGI server,
with Redis as the channel layer:

```bash
# example
daphne -b 0.0.0.0 -p 8001 config.asgi:application
# or: uvicorn config.asgi:application --host 0.0.0.0 --port 8001
```

Put it behind nginx and forward the WebSocket upgrade headers:

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

The WSGI entry point (`config/wsgi.py`, `WSGI_APPLICATION`) is left in place for
any WSGI-only deployment — the app still runs there, just without live push
(polling fallback).

## Failure behaviour (why this is safe)

Real-time is strictly an enhancement:

- `realtime.py` swallows every error and no-ops when the channel layer is absent.
- Producers wrap the push in `try/except` — a message still saves, a notification
  is still created, even if the push fails.
- Clients fall back to polling on socket error/close and retry the connection
  with a short back-off.

So you can deploy the code with `WEBSOCKETS_ENABLED=false` and no ASGI server and
nothing regresses; turning it on is purely additive.
