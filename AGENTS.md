# Python Service Agent Guidelines (L1 Extension)

Inherits: Universal L0 Invariants (workflow/AGENTS.md).
Do not repeat global workflow rules here. Module map: `ARCHITECTURE.md`.
This is the only agent instruction file. Claude Code, Codex, Cursor, Copilot and Gemini read it. Do not add CLAUDE.md, GEMINI.md or other per-tool copies: Claude Code ignores this file once a CLAUDE.md exists. `make policy` rejects them.

## 1. Stack

- Python (version in `.python-version`) managed by uv
- FastAPI with Pydantic v2; async SQLAlchemy 2 with asyncpg; Alembic migrations
- Ruff, Mypy (strict), pytest with pytest-asyncio and httpx
- Every command goes through the Makefile; `make help` lists targets

## 2. Where things go

- Look up the module you need in the Code map in `ARCHITECTURE.md` before writing a helper.
- Feature code: one module per feature under `src/app/models`, `src/app/schemas` and `src/app/api/v1/endpoints`, registered in `src/app/api/v1/router.py`.
- Tests: `tests/test_<feature>.py`, using the `client` fixture from `tests/conftest.py`.
- Nest new code freely inside existing top-level directories. A new top-level directory needs a `layout.allow` entry in `scripts/repo-policy.json`; record the reason in `docs/decisions/` if it changes the architecture.
- A new dependency needs a row in `docs/dependencies.md`. Declare tool versions only in the `dev` group of `pyproject.toml` or in a Makefile or workflow variable with a `renovate:` comment.

## 3. Runtime Invariants

- Read environment variables only in `src/app/core/config.py` [enforced by ast-grep].
- Take identity with `owner_id: OwnerId`; never default it. Bearer tokens validate against the JWKS; the `x-user-id` header is dev-only [enforced by tests]. Filter every query by `owner_id` [enforced by tests].
- Inject sessions with `db: DbSession`; endpoints own the commit [review-only].
- Return typed Pydantic models, never ORM instances [review-only].
- Use `select(Model)` with `AsyncSession`; the legacy query API is banned [review-only].
- Error bodies are `{"detail": ...}` and never include internals [review-only].
- Replace markers named `TEMPLATE-TODO` only when you own the decision; `make template-debt` lists them.

## 4. Verification Gates

`make check` runs all six; `make verify` is the fast subset used by agent hooks.

1. Gate 1 (Typecheck): `make typecheck`
2. Gate 2 (Lint & Format): `make lint` (Ruff including `S` rules, Markdown)
3. Gate 3 (Tests): `make test`
4. Gate 4 (Dead Code): `make dead-code`
5. Gate 5 (Duplication): `make duplication` (jscpd, zero clones)
6. Gate 6 (Anti-Slop): `make anti-slop`

CI also runs `make licenses`, `make security` and `make spec-check`. Regenerate
the contract with `make openapi` and `make client` after route changes.
