.PHONY: setup dev test lint fix typecheck check up down db-migrate db-revision

setup:
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

fix:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run mypy src

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy src
	uv run pytest
	npx --yes --package @ast-grep/cli ast-grep scan
