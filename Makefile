.PHONY: install dev test lint lint-fix typecheck check db-migrate db-revision

install:
	uv sync --all-groups

dev:
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

lint-fix:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy src

check:
	uv run mypy src
	uv run ruff check .
	uv run ruff format --check .
	uv run pytest
	npx --yes fallow@3.33.1 dupes --quiet --no-fragments
	npx --yes --package @ast-grep/cli ast-grep scan

db-migrate:
	uv run alembic upgrade head

db-revision:
	uv run alembic revision --autogenerate -m "$(m)"
