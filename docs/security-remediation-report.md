# AryaCrypt Security Remediation Report

**Date:** 2026-08-31  
**Scope:** Implement audit fixes C1, H1–H8, M1–M13 without changing Spec v1.1.0 crypto (RomanMapper → PBKDF2 600k → AES-256-GCM / `.arya` layout).

## Verdict

Core vault crypto is unchanged and vector-compatible. Auth/session hardening, upload limits, logging scrubbing, SDK validation parity, and frontend token storage are in place. Suitable for staged production **after** setting a strong `SECRET_KEY`, enabling `REFRESH_COOKIE_SECURE` on HTTPS, tightening CSP `connect-src` to your API origin, and running Alembic on Postgres.

## Test results (this run)

| Suite | Result |
|-------|--------|
| Python SDK | 10 passed |
| Node SDK | 10 passed |
| Cross-language `scripts/cross_compat_test.py` | OK |
| Backend (incl. security) | 18 passed |
| Frontend `npm run build` | OK |
| Alembic `b2c3d4e5f6a7` | Applied on local Postgres |

## Fixes delivered

### Critical / High
- **C1** — `SECRET_KEY` validated at startup (min length, placeholder reject); `.env.example` documents `openssl rand -hex 32`.
- **H1** — Access tokens require `type=access`; refresh requires `type=refresh`; `tv` matched to `user.token_version`.
- **H2** — `files.py` no longer logs keys/salt/nonce/tag/password/streams.
- **H3** — Python SDK `decrypt_stream` writes to private temp, copies out only after GCM verify, always unlinks.
- **H4** — Node preprocess password length uses Unicode code points (`[...password].length`).
- **H5** — Upload size: `Content-Length` + streaming `LimitedReader`; HTTP 413.
- **H6** — Durable refresh revocation table (hashed tokens); logout/refresh rotate+revoke.
- **H7** — Password change increments `token_version` (invalidates outstanding JWTs).
- **H8** — SPA: access token in memory; refresh via HttpOnly cookie + `withCredentials`; CSP meta; `VITE_API_BASE_URL`; see `docs/auth-session.md`.

### Medium (selected)
- SDK: exact salt length, strict Base64, legacy encrypt validation, salt/nonce checks on decrypt (Node + Python).
- Path jail under `UPLOAD_DIR`; vault capacity check; history `limit` cap; generic 500 messages; orphan `.arya` unlink on DB fail; decrypt temp `finally`.
- CORS explicit origins + credentials; auth/decrypt rate limits; `cryptography` upper bound in python-sdk; CI expanded (`.github/workflows/ci.yml`).

## Key files touched

- Backend: `config.py`, `security.py`, `deps.py`, `auth.py`, `files.py`, `middleware.py`, `rate_limit.py`, models/migration, tests
- Frontend: `tokenStore.ts`, `api.ts`, `auth.service.ts`, `App.tsx`, `index.html`, Settings redirect after password change
- SDKs: format/kdf/preprocess/`AryaCrypt` (Node), aes_gcm/format/kdf/api (Python)
- Docs: `docs/auth-session.md`, this report

## Remaining / production notes

1. Login/refresh JSON still includes `refresh_token` for non-browser clients; SPA ignores it—prefer cookie-only responses later if you can break API clients.
2. Rate limits are process-local; use a shared store behind multiple workers.
3. Set `REFRESH_COOKIE_SECURE=true` and HTTPS in production; update CSP `connect-src` for the real API host.
4. Confirm Postgres has migration `b2c3d4e5f6a7` on every environment.
5. Rotate any previously committed/shared JWT secrets.

## Crypto compatibility

Spec v1.1.0 algorithms, RomanMapper, PBKDF2 params, AES-GCM, and `.arya` containers were **not** changed. Existing vectors and cross-language decrypt still pass.
