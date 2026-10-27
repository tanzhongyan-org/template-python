"""Oversized request bodies are rejected with 413."""

from collections.abc import AsyncIterator

from httpx import AsyncClient

from app.core.config import settings

HEADERS = {"x-user-id": "owner-body"}


async def test_declared_oversized_body_returns_413(client: AsyncClient) -> None:
    body = b'{"title": "t", "body": "' + b"x" * settings.max_request_body_bytes + b'"}'
    response = await client.post(
        "/api/v1/notes/",
        content=body,
        headers={**HEADERS, "content-type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}


async def test_streamed_oversized_body_returns_413(client: AsyncClient) -> None:
    async def chunks() -> AsyncIterator[bytes]:
        yield b'{"title": "t", "body": "'
        for _ in range(settings.max_request_body_bytes // 1024 + 1):
            yield b"x" * 1024
        yield b'"}'

    response = await client.post(
        "/api/v1/notes/",
        content=chunks(),
        headers={**HEADERS, "content-type": "application/json"},
    )
    assert response.status_code == 413


async def test_body_within_limit_is_accepted(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/notes/", json={"title": "ok", "body": "x" * 1000}, headers=HEADERS
    )
    assert response.status_code == 201
