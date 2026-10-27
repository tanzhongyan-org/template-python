# Python Runtime Agent Guidelines (L1 Extension)

Inherits: Universal L0 Invariants (workflow/AGENTS.md).
Do not repeat global workflow rules here.

## 1. Project Technology Stack
- Runtime: Python 3.12+ managed by uv
- Framework: FastAPI with Pydantic v2
- Database: Async SQLAlchemy 2.0+ with asyncpg
- Migrations: Alembic (async configuration)
- Configuration: Pydantic BaseSettings in `src/app/core/config.py`
- Testing & Quality: Ruff, Mypy (strict), Pytest with pytest-asyncio and httpx

## 2. Architecture & File Placement
- Configuration: Singleton settings in `src/app/core/config.py`
- Database Engine: Async engine & async_sessionmaker in `src/app/core/database.py`
- Database Models: Subclasses of Base in `src/app/models/<feature>.py`
- Schemas & DTOs: Request/Response Pydantic models in `src/app/schemas/<feature>.py`
- API Routers: Feature routes in `src/app/api/v1/endpoints/<feature>.py`, registered in `router.py`
- Migrations: Version scripts in `alembic/versions/` configured via `alembic.ini` and `alembic/env.py`
- Test Suites: Async tests in `tests/test_<feature>.py` using `AsyncClient` from `conftest.py`

## 3. Runtime & Async Invariants
- Asynchronous Engine & Lifespan: Manage engine lifecycle via FastAPI lifespan context manager (`await engine.dispose()`) [review-only].
- Modern SQLAlchemy 2.0+ Queries: Use `select(Model)` and `AsyncSession`. Legacy query API is banned [review-only].
- Session Scope: Inject sessions via `Depends(get_db)`. Endpoints control transaction commit boundaries [review-only].
- Asynchronous Testing: Test endpoints using `httpx.AsyncClient` with `ASGITransport(app=app)` [enforced by test runner].
- Typed DTO Returns: Endpoints return typed Pydantic models (`from_attributes=True`), never raw ORM model instances [review-only].

## 4. Verification Gates
Run `make check` to verify task completion:
1. Gate 1 (Typecheck): `uv run mypy src`
2. Gate 2 (Lint & Format): `uv run ruff check . && uv run ruff format --check .`
3. Gate 3 (Tests): `uv run pytest`
4. Gate 4 (Dead Code): Covered by Pyflakes in Gate 2 (`ruff check .`)
5. Gate 5 (Duplication): N/A (TypeScript/Web specific)
6. Gate 6 (Anti-Slop): `npx --yes --package @ast-grep/cli ast-grep scan`
