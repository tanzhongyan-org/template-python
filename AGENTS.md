# Python Runtime Agent Guidelines (L1 Extension)

Inherits: Universal L0 Invariants (workflow/AGENTS.md).
Do not repeat global workflow rules here.

## 1. Project Technology Stack
- Runtime: Python 3.11+ managed by uv
- Framework: FastAPI with Pydantic v2
- Settings: Validated via src/app/core/config.py (Pydantic BaseSettings)
- Testing & Linting: Ruff, Mypy (strict), Pytest

## 2. Physical File Placement Rules
- Transport Endpoints: Place in src/app/api/v1/<feature>.py
- Domain Boundaries: Place in src/app/domain/<feature>/ (schemas.py, service.py, repository.py)
- Configuration: Singleton settings in src/app/core/config.py
- Test Suites: Place in tests/test_<feature>.py mirroring public entry points

## 3. Data Access & Boundary Invariants
- Direct access to os.environ in domain logic is strictly banned. Import settings from app.core.config.
- API endpoints parse and validate inputs via Pydantic schemas before calling domain services.
- Domain services return typed DTOs/schemas, not raw database rows.

## 4. The 6 Verification Gates
Run these commands to prove task completion:
1. Gate 1 (Typecheck): uv run mypy src
2. Gate 2 (Lint & Format): uv run ruff check . && uv run ruff format --check .
3. Gate 3 (Tests): uv run pytest
4. Gate 4 (Dead Code): Clean imports and zero unused endpoints
5. Gate 5 (Duplication): npx --yes fallow@3.33.1 dupes --quiet --no-fragments
6. Gate 6 (Anti-Slop): npx --yes --package @ast-grep/cli ast-grep scan
