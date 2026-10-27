# renovate: datasource=npm depName=jscpd
JSCPD_VERSION := 5.4.2
# renovate: datasource=npm depName=markdownlint-cli2
MARKDOWNLINT_VERSION := 0.24.0
# renovate: datasource=pypi depName=schemathesis
SCHEMATHESIS_VERSION := 4.32.6

.DEFAULT_GOAL := help

.PHONY: help setup up down dev db-migrate db-revision test lint fix typecheck dead-code \
	duplication anti-slop policy audit template-debt dast verify check

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
	uv run vulture src .vulture-whitelist.py --min-confidence 80

duplication: ## Gate 5: jscpd
	npx --yes jscpd@$(JSCPD_VERSION)

anti-slop: ## Gate 6: ast-grep rules and rule tests
	uv run ast-grep scan
	uv run ast-grep test --skip-snapshot-tests

policy: ## Layout, docs, dependency ledger and version drift checks
	node scripts/repo-policy.mjs all

audit: ## Dependency vulnerability scan (uv audit)
	uv audit --locked --preview-features audit-command

template-debt: ## List TEMPLATE-TODO markers a derived repo must resolve
	@git grep -n "TEMPLATE-TODO[(]" || true

dast: ## Schemathesis against a running server (BASE_URL, default http://localhost:8000)
	uvx schemathesis@$(SCHEMATHESIS_VERSION) run "$${BASE_URL:-http://localhost:8000}/openapi.json" \
		--header "x-user-id: dast" --max-examples 25 --exclude-checks positive_data_acceptance,allow_header_conformance

verify: typecheck lint anti-slop policy ## Fast checks without a database
	@echo "verify: ok"

check: lint typecheck test dead-code duplication anti-slop policy ## All gates, as run in CI
	@echo "check: ok"
