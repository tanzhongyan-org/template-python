# Python Runtime Template

Universal Python application template with agentic quality guardrails and verification gates.

## Features

- **Runtime:** Python 3.11+ managed by [uv](https://docs.astral.sh/uv/)
- **Framework:** FastAPI with domain-colocated architecture
- **Config & Validation:** Centralized Pydantic Settings & Request/Response schemas
- **Code Quality:** Ruff (lint & format), Mypy (strict typechecking), and Pytest
- **Agent Guardrails:**
  - `lefthook.yml`: Sub-second local Git pre-commit hooks
  - `fallow.jsonc`: AST-aware code duplication and cognitive complexity limits
  - `sgconfig.yml` + `.ast-grep/`: Automatic detection of placeholder stubs and unfulfilled code
  - `.github/workflows/ci.yml`: Automated CI running the 6 Universal Verification Gates
  - `AGENTS.md`: Runtime-specific agent invariants

## Getting Started

### 1. Create a New Repository
Click **"Use this template"** on GitHub or use the GitHub CLI:
```bash
gh repo create my-service --template tanzhongyan-org/template-python --private --clone
cd my-service
```
*(On first push to `main`, GitHub Actions automatically renames all template placeholders to your new repository name and self-deletes the initialization workflow).*

### 2. Local Setup
```bash
# Sync virtualenv and dependencies
uv sync --all-groups

# Start development server
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Run Verification Gates
```bash
# Gate 1: Typecheck
uv run mypy src

# Gate 2: Lint & Format
uv run ruff check .
uv run ruff format --check .

# Gate 3: Test
uv run pytest

# Gate 5: Duplication Audit
npx --yes fallow@3.33.1 dupes --quiet --no-fragments

# Gate 6: Anti-Slop Scan
npx --yes --package @ast-grep/cli ast-grep scan
```
