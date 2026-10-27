# 0002. Python service stack

## Context

This template starts HTTP services backed by Postgres. The stack has to be async end to end, fully typed, and easy for agents and people to extend one feature at a time.

## Decision

- Python 3.14, pinned in `.python-version`. 3.12 receives security fixes only, and 3.15 is too new for the wheels this stack needs.
- uv manages the interpreter, the virtual environment and the lock file.
- FastAPI with Pydantic v2 for the HTTP layer.
- SQLAlchemy 2 async with asyncpg, and Alembic for migrations.
- Postgres 18, pinned in `compose.yaml` and in CI.
- Ruff for lint and format, Mypy in strict mode, pytest for tests.

## Consequences

- Handlers are coroutines, and every database call is awaited.
- Upgrading Python is a one-line change in `.python-version` plus the Ruff and Mypy targets in `pyproject.toml`.
- Sync-only libraries need an executor or a replacement.
- Postgres major upgrades change the tag in `compose.yaml` and `.github/workflows/ci.yml` together; `make policy` fails if they disagree.
