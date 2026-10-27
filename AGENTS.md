# Python Runtime Agent Guidelines (L0)

## 1. Universal Architectural Invariants
- **Domain Colocation over Technical Grab-Bags:** Organize code strictly by cohesive domain boundaries (`src/app/domain/<feature>/`). Never create generic `utils/`, `helpers/`, or `misc/` directories.
- **Unidirectional Layering:** Dependencies flow in one direction:
  `Transport (API routers) -> Domain Services -> Persistence (Repositories) / External Integrations`
- **Boundary Validation:** Direct reads of `os.environ` in domain logic are strictly banned. Centralize and validate all environment variables inside `src/app/core/config.py` using Pydantic `BaseSettings`.
- **Search-Before-Author:** Search existing modules before authoring helpers or math functions. Parameterize existing code; fork-and-duplicate is strictly prohibited.

## 2. Directory Layout
```
src/app/
├── api/
│   └── v1/                      # Transport: FastAPI routers & endpoints
├── domain/                      # Cohesive Domain Boundaries (Colocated)
│   └── <feature>/
│       ├── schemas.py           # Pydantic request/response validation schemas
│       ├── service.py           # Pure business logic & transactions
│       └── repository.py        # Data access layer
└── core/                        # Infrastructure & Config
    └── config.py                # Pydantic BaseSettings singleton
tests/                           # Test suite (mirrors entry points)
```

## 3. The 6 Verification Gates
Before claiming task completion or creating PRs, all gates must pass:
1. **Typecheck:** `uv run mypy src` (0 errors)
2. **Lint & Format:** `uv run ruff check .` and `uv run ruff format --check .` (0 warnings)
3. **Tests:** `uv run pytest` (Full suite green)
4. **Dead Code:** Clean imports and zero unused endpoints
5. **Duplication Audit:** `npx --yes fallow@3.33.1 dupes --quiet --no-fragments`
6. **Anti-Slop Scan:** `npx --yes --package @ast-grep/cli ast-grep scan`
