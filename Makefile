# renovate: datasource=npm depName=jscpd
JSCPD_VERSION := 5.4.2
# renovate: datasource=npm depName=markdownlint-cli2
MARKDOWNLINT_VERSION := 0.24.0
# renovate: datasource=pypi depName=schemathesis
SCHEMATHESIS_VERSION := 4.32.6
# renovate: datasource=npm depName=@hey-api/openapi-ts
OPENAPI_TS_VERSION := 0.99.0
# Stay on TypeScript 5: @hey-api/openapi-ts 0.99 crashes with TS 6/7.
# renovate: datasource=npm depName=typescript
TYPESCRIPT_VERSION := 5.9.3
OPENAPI_TS_NPX := npx --yes --package=@hey-api/openapi-ts@$(OPENAPI_TS_VERSION) \
	--package=typescript@$(TYPESCRIPT_VERSION)

.DEFAULT_GOAL := help

.PHONY: help setup up down dev db-migrate db-revision test lint fix typecheck dead-code \
	duplication anti-slop policy audit licenses security openapi client spec-check \
	template-debt dast verify check

help: ## List public make targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /\t/' | sort

setup: ## Install dependencies and git hooks
	uv sync --locked --all-groups
	uv run lefthook install

up: ## Start Postgres and wait until it is healthy
	docker compose up -d --wait

down: ## Stop Postgres
	docker compose down

dev: up db-migrate ## Start Postgres, migrate, run the server with reload
	uv run uvicorn app.main:app --reload --port 8000

db-migrate: ## Apply Alembic migrations
	uv run alembic upgrade head

db-revision: ## Create a migration: make db-revision m="add_table"
	uv run alembic revision --autogenerate -m "$(m)"

test: ## Run the test suite (needs Postgres)
	uv run pytest

lint: ## Ruff lint, Ruff format check, Markdown lint
	uv run ruff check .
	uv run ruff format --check .
	npx --yes markdownlint-cli2@$(MARKDOWNLINT_VERSION)

fix: ## Apply Ruff fixes and formatting
	uv run ruff check --fix .
	uv run ruff format .

typecheck: ## Mypy in strict mode
	uv run mypy src

dead-code: ## Gate 4: vulture
	uv run vulture src --min-confidence 80

duplication: ## Gate 5: jscpd
	npx --yes jscpd@$(JSCPD_VERSION) --format python --min-tokens 50 --threshold 0 \
		--ignore "**/tests/**,**/alembic/versions/**,**/__pycache__/**" --reporters console src

anti-slop: ## Gate 6: ast-grep rules and rule tests
	uv run ast-grep scan
	uv run ast-grep test --skip-snapshot-tests

policy: ## Layout, docs, dependency ledger and version drift checks
	node scripts/repo-policy.mjs all

audit: ## Dependency vulnerability scan (uv audit)
	uv audit --locked --preview-features audit-command

licenses: ## Check runtime licences and regenerate NOTICE
	uv run python scripts/check_licenses.py

security: audit ## Gitleaks, vulnerability audit and new-dependency check
	if command -v gitleaks >/dev/null 2>&1; then gitleaks detect --no-banner --redact; else echo 'gitleaks is not installed; CI runs the history scan. See .github/CONTRIBUTING.md (Prerequisites)' >&2; fi
	uv run python scripts/check_new_deps.py

openapi: ## Export the committed OpenAPI document to clients/openapi.json
	uv run python scripts/export_openapi.py

client: openapi ## Generate the TypeScript client from the committed spec
	$(OPENAPI_TS_NPX) openapi-ts -i ./clients/openapi.json -o ./clients/ts -p @hey-api/client-fetch

spec-check: ## Fail when the committed spec or TS client is stale
	uv run python scripts/check_spec.py
	tmp=$$(mktemp -d); trap 'rm -rf "$$tmp"' EXIT; \
		$(OPENAPI_TS_NPX) openapi-ts -i ./clients/openapi.json -o "$$tmp/ts" -p @hey-api/client-fetch \
		&& diff -r clients/ts "$$tmp/ts"

template-debt: ## List TEMPLATE-TODO markers a derived repo must resolve
	@git grep -n "TEMPLATE-TODO[(]" || true

dast: ## Schemathesis against a running server (BASE_URL, default http://localhost:8000)
	uvx schemathesis@$(SCHEMATHESIS_VERSION) run "$${BASE_URL:-http://localhost:8000}/openapi.json" \
		--header "x-user-id: dast" --max-examples 25 --exclude-checks positive_data_acceptance,allow_header_conformance

verify: typecheck lint anti-slop policy ## Fast checks without a database
	@echo "verify: ok"

check: lint typecheck test dead-code duplication anti-slop policy spec-check ## All gates, as run in CI
	@echo "check: ok"
