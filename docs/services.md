# Service ladder

Each production concern from the baseline resolves to one managed default,
with a local stand-in that needs no paid account. `make dev` brings a fresh
clone up with only `.env.example` filled in.

| Concern | Production | Local dev | Status |
| --- | --- | --- | --- |
| Database | Managed Postgres over `DATABASE_URL` | One Postgres container via `make up` | Built |
| Auth | Product Better Auth; this service validates bearer tokens against the product JWKS | Dev `x-user-id` header behind the guard in `src/app/core/auth.py` | Built |
| Email | Resend HTTP API | Log to the console when no key is set | `TEMPLATE-TODO(service)`: add the sender |
| Files | S3-compatible private bucket | A dev bucket | `TEMPLATE-TODO(service)`: add the client |
| Analytics | PostHog Cloud, server-side events | Off | `TEMPLATE-TODO(service)`: add the tracker |
| Errors and traces | Sentry | Off | `TEMPLATE-TODO(service)`: add the SDK |
| Uptime | Better Stack on `/api/v1/health` | — | `TEMPLATE-TODO(service)`: register the check |

Rules for anything added here:

- Prefer a managed free tier with an official SDK. A local stand-in is one
  container or a console fallback. Self-host only when it removes code or
  cost, and record a one-line reason for any paid tier or vendor-only API.
- Every new service gets a dev fallback in the same PR, so `make dev` keeps
  working with no extra keys.
- Secrets arrive through `src/app/core/config.py` only, with a row in the
  `README.md` configuration table and a key in `.env.example`.
