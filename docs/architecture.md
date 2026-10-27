# Architecture

## Overview
High-performance Python backend template powered by FastAPI, SQLAlchemy 2.0 (asyncio), asyncpg, Pydantic v2, and Alembic.

## Directory Structure
- `src/app/api/`: FastAPI route controllers and routers
- `src/app/core/`: Configuration, database engine/session lifecycle
- `src/app/models/`: SQLAlchemy 2.0 mapped models
- `src/app/schemas/`: Pydantic v2 request/response schemas
- `alembic/`: Database migrations
- `docs/`: Architecture, specifications, plans, and architectural decisions
