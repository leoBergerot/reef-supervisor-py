## Summary

Adds Cloudflare Turnstile server-side verification and in-memory rate limiting on FastAPI auth endpoints so the Vite app (PR #61, `turnstileToken`) can talk to this API.

### Protected routes
- `POST /token` — OAuth2 password form; accepts extra form field `turnstileToken`
- `POST /users` — JSON body; accepts `turnstileToken` on `UserCreateRequest`

### Behavior
- When `TURNSTILE_ENABLED=true`, missing token → **400**, failed siteverify → **403**
- When `TURNSTILE_ENABLED=false` (local/dev default), verification is skipped
- Rate limit: **~10 requests/minute/IP** on those two routes only (in-memory sliding window)
- Client IP: `CF-Connecting-IP` → `X-Forwarded-For` → socket peer

### Deploy env vars
| Name | Notes |
| --- | --- |
| `TURNSTILE_ENABLED` | `true` in prod; `false` for local/dev |
| `TURNSTILE_SECRET_KEY` | Cloudflare Turnstile secret (API only) |

Local compose sets `TURNSTILE_ENABLED=false`. Prod compose defaults enabled and expects `TURNSTILE_SECRET_KEY`.

### Tests
- New `app/test_turnstile_auth.py`: skip when disabled, reject when enabled without/invalid token (mocked siteverify), rate-limit 429
