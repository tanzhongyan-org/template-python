.PHONY: install up down dev test lint lint-fix typecheck check db-migrate db-revision

install:
	uv sync --all-groups

up:
	docker compose up -d --wait

down:
	docker compose down

dev: up db-migrate
	uv run uvicorn app.main:app --reload --port 8000

db-migrate:
	uv run alembic upgrade head

db-revision:
	uv run alembic revision --autogenerate -m "$(m)"

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

check: lint typecheck test
	npx --yes fallow@3.33.1 dupes --root . --quiet --no-fragments
	npx --yes --package @ast-grep/cli ast-grep scan
