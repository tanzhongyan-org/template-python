"""API v1 router definition."""

from fastapi import APIRouter

from app.api.v1.endpoints import health, notes

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["Health"])
api_v1_router.include_router(notes.router, prefix="/notes", tags=["Notes"])

router = api_v1_router
