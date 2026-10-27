# Python Runtime Agent Guidelines (L1 Extension)

Inherits: Universal L0 Invariants (workflow/AGENTS.md).
Do not repeat global workflow rules here.

## 1. Project Technology Stack
- Runtime: Python 3.11+ managed by uv
- Framework: FastAPI with Pydantic v2
- Database: Async SQLAlchemy 2.0 + asyncpg
- Migrations: Alembic (async configuration)
- Settings: Validated via src/app/core/config.py (Pydantic BaseSettings)
- Testing & Linting: Ruff, Mypy (strict), Pytest

## 2. Physical File Placement Rules
- Configuration: Singleton settings in src/app/core/config.py
- Database Engine: Async engine and session maker in src/app/core/database.py
- Database Models: Place in src/app/models/ (Base DeclarativeBase in base.py)
- Schemas & DTOs: Place in src/app/schemas/ (request and response models)
- Transport Endpoints: Place in src/app/api/v1/endpoints/<feature>.py
- Router Aggregation: Centralized in src/app/api/v1/router.py, mounted in src/app/main.py
- Migrations: Place migration versions in alembic/versions/ configured via alembic.ini and alembic/env.py
- Test Suites: Place in tests/test_<feature>.py mirroring public entry points

## 3. Data Access & Boundary Invariants
- Asynchronous Database Operations: All DB operations must use SQLAlchemy 2.0 2.0-style queries (e.g. `select(Model)`) with `AsyncSession`. Legacy query API is banned.
- Session Lifecycle: Endpoints inject sessions via `Depends(get_db)` from `app.core.database`.
- Direct access to `os.environ` in application logic is strictly banned. Import settings from `app.core.config`.
- API endpoints parse and validate inputs via Pydantic schemas before executing database operations.
- API endpoints return typed Pydantic DTOs/schemas (`from_attributes=True`), never raw database model instances.
- Migration Discipline: Any schema or model change requires an accompanying Alembic migration in alembic/versions/.

## 4. The 6 Verification Gates
Run these commands to prove task completion:
1. Gate 1 (Typecheck): uv run mypy src
2. Gate 2 (Lint & Format): uv run ruff check . && uv run ruff format --check .
3. Gate 3 (Tests): uv run pytest
4. Gate 4 (Dead Code): Clean imports and zero unused endpoints
5. Gate 5 (Duplication): npx --yes fallow@3.33.1 dupes --quiet --no-fragments
6. Gate 6 (Anti-Slop): npx --yes --package @ast-grep/cli ast-grep scan
