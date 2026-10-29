# Dependency ledger

One row per direct dependency in `pyproject.toml`. `make policy` fails when a dependency has no row or a row has no dependency.

## Runtime

| Dependency | Purpose | Why the default was not enough | Replaced |
| --- | --- | --- | --- |
| `fastapi` | HTTP routing, request validation, OpenAPI document | The standard library has no routing, validation or OpenAPI output | Starting point |
| `uvicorn` | ASGI server | FastAPI needs an ASGI server; the `standard` extra adds uvloop and httptools for speed | Starting point |
| `pydantic` | Request and response models | Dataclasses do not validate or coerce input | Starting point |
| `pydantic-settings` | Typed settings from the environment and `.env` | `os.environ` gives untyped strings and scatters reads across modules | Starting point |
| `sqlalchemy` | ORM and query builder, async sessions | `sqlite3` and raw drivers give no model mapping or typed queries | Starting point |
| `asyncpg` | Async Postgres driver | SQLAlchemy needs a driver, and this one is async-native | Starting point |
| `alembic` | Schema migrations | `create_all` cannot change an existing schema | Starting point |
| `pyjwt` | Verifies product bearer tokens against the JWKS | The standard library has no JWT verification | Added for product JWT validation |
| `cryptography` | RSA and ECDSA signature checks behind PyJWT | Pure-Python crypto is slow and unsafe to hand-roll | Added for product JWT validation |

## Development

| Dependency | Purpose | Why the default was not enough | Replaced |
| --- | --- | --- | --- |
| `pytest` | Test runner | `unittest` has no fixtures or parametrization of this kind | Starting point |
| `pytest-asyncio` | Runs async tests | pytest cannot await coroutines alone | Starting point |
| `httpx` | In-process API client for tests | `urllib` has no ASGI transport | Starting point |
| `ruff` | Lint, format and security rules | Replaces several separate linters and a formatter | Starting point |
| `mypy` | Strict type checking | Python does not check types at run time | Starting point |
| `vulture` | Dead code gate | Ruff does not find unused module-level code | Starting point |
| `ast-grep-cli` | Anti-slop rules | Ruff cannot express project-specific structural rules | `npx` call in the Makefile |
| `lefthook` | Git hooks | Raw `.git/hooks` scripts are not shared through git | `npx` call in the Makefile |
| `zizmor` | Workflow security lint | No other tool in the stack reads workflow files | Starting point |
| `pip-licenses` | Lists installed licences for `make licenses` | `importlib.metadata` does not report licences consistently | Added for the licence gate |
