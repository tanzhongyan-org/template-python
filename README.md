# template-python

[![CI](https://github.com/tanzhongyan-org/template-python/actions/workflows/ci.yml/badge.svg)](https://github.com/tanzhongyan-org/template-python/actions/workflows/ci.yml)
[![CodeQL](https://github.com/tanzhongyan-org/template-python/actions/workflows/codeql.yml/badge.svg)](https://github.com/tanzhongyan-org/template-python/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A GitHub template for a FastAPI service on async SQLAlchemy and Postgres. It is for developers who start a new Python API and want the quality gates, security scans and agent hooks in place on day one.

## Quick start

You need these installed. See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for versions.

- GNU make. On Windows run `winget install ezwinports.make`; on macOS run `xcode-select --install`.
- Docker, for the local Postgres.
- [uv](https://docs.astral.sh/uv/), which installs the Python runtime, and Node.

If port 5432 is already taken, set `POSTGRES_PORT` in `.env` and point `DATABASE_URL` at the same port. To skip the agent stop hook for one session, set `AGENT_HOOK_SKIP=1`.

```bash
gh repo create my-service --template tanzhongyan-org/template-python --private --clone
cd my-service
make setup
cp .env.example .env
make dev
```

In a second terminal:

```bash
curl http://localhost:8000/api/v1/health
```

You should see JSON like `{"status":"healthy","app_name":"my-service","environment":"development",...}`.

## What you get

- FastAPI with Pydantic v2, async SQLAlchemy 2, asyncpg and Alembic migrations.
- An example notes API that isolates data per owner, with tests.
- Identity that fails closed: product bearer tokens validate against the JWKS, and the dev `x-user-id` header works only in development and test.
- A request body size limit that returns HTTP 413.
- Six gates plus a spec diff behind `make check`: Mypy, Ruff, pytest, vulture, jscpd, ast-grep and the OpenAPI contract check.
- `make licenses` and `make security` for the licence and supply-chain gates.
- A committed OpenAPI spec with a generated TypeScript client in `clients/`.
- CI through thin callers to the shared workflows: gates, CodeQL, gitleaks, `uv audit`, dependency review and zizmor, plus a weekly Schemathesis run.
- Hooks for Claude Code and Gemini CLI that run `make verify` before an agent ends its turn.

## After creating your repo

1. The **Initialize Template Repository** workflow runs on your first push to `main` (or run it from the Actions tab). It renames the template placeholders and opens a "Template follow-ups" issue.
2. List what you still have to change:

```bash
make template-debt
```

You should see one line per marker, such as the auth stub in `src/app/core/auth.py`.

## Configuration

Settings load from the environment or a `.env` file through `src/app/core/config.py`.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `APP_NAME` | no | `template-python` | Service name shown in the OpenAPI title and health response. |
| `APP_ENV` | no | `development` | Runtime environment name. |
| `DEBUG` | no | `false` | Echo SQL statements when `true`. |
| `DATABASE_URL` | yes | local Postgres | Async SQLAlchemy URL, `postgresql+asyncpg://...`. |
| `TRUST_IDENTITY_HEADER` | no | `false` | Accept the `x-user-id` header as the caller identity in development and test. The app refuses to boot with it set anywhere else. |
| `JWKS_URL` | no | unset | Product JWKS document for bearer validation. While unset, bearer tokens are rejected. |
| `JWT_ISSUER` | no | unset | Expected token issuer. Required with `JWKS_URL`. |
| `JWT_AUDIENCE` | no | unset | Expected token audience. Required with `JWKS_URL`. |
| `POSTGRES_PORT` | no | `5432` | Host port for the Postgres container in `compose.yaml`. Change it when 5432 is in use. |
| `MAX_REQUEST_BODY_BYTES` | no | `1048576` | Largest accepted request body. Larger bodies return 413. |

## Commands

Run `make help` for the same list.

| Command | What it does |
| --- | --- |
| `make setup` | Install dependencies and git hooks. |
| `make up` / `make down` | Start or stop Postgres. |
| `make dev` | Start Postgres, migrate, run the server with reload. |
| `make db-migrate` | Apply Alembic migrations. |
| `make db-revision m="name"` | Create a migration from model changes. |
| `make test` | Run the tests. Needs Postgres. |
| `make lint` / `make fix` | Check or fix Ruff and Markdown. |
| `make typecheck` | Mypy in strict mode. |
| `make dead-code` | vulture. |
| `make duplication` | jscpd. |
| `make anti-slop` | ast-grep rules and rule tests. |
| `make policy` | Layout, docs, dependency ledger and version drift checks. |
| `make audit` | `uv audit` for known vulnerabilities. |
| `make licenses` | Licence gate; regenerates `NOTICE`. |
| `make security` | Gitleaks, `uv audit` and the new-dependency check. |
| `make openapi` / `make client` | Export the spec; generate the TS client. |
| `make spec-check` | Fail when the committed spec or client is stale. |
| `make dast` | Schemathesis against a running server. |
| `make template-debt` | List markers a derived repo must resolve. |
| `make verify` | Fast checks without a database. |
| `make check` | Every gate, as CI runs them. |

## Project layout

| Path | Contents |
| --- | --- |
| `src/app/` | Application code. |
| `alembic/` | Database migrations. |
| `tests/` | Tests that call the API through `httpx`. |
| `clients/` | Committed OpenAPI spec and generated TypeScript client. |
| `scripts/` | Policy checker, gate scripts and agent hook. |
| `docs/` | Decisions, services and the dependency ledger. See [docs/README.md](docs/README.md). |
| `.github/` | Workflows, issue forms, CODEOWNERS and the branch ruleset export. |

[ARCHITECTURE.md](ARCHITECTURE.md) maps each module. Read [CONTRIBUTING.md](.github/CONTRIBUTING.md) before you open a PR, [SECURITY.md](.github/SECURITY.md) to report a vulnerability, and [LICENSE](LICENSE) for terms.
