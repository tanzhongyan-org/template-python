"""Inputs Postgres cannot store are rejected with 422, not a 500."""

import pytest
from httpx import AsyncClient

HEADERS = {"x-user-id": "owner-hardening", "content-type": "application/json"}


@pytest.mark.parametrize("note_id", [0, 2_147_483_648, 2**70])
async def test_out_of_range_note_id_returns_422(client: AsyncClient, note_id: int) -> None:
    response = await client.get(f"/api/v1/notes/{note_id}", headers=HEADERS)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        b'{"title": "bad\\u0000title", "body": ""}',
        b'{"title": "lone \\ud800 surrogate", "body": ""}',
        b'{"title": "ok", "body": "nul \\u0000"}',
    ],
)
async def test_unstorable_text_returns_422(client: AsyncClient, payload: bytes) -> None:
    response = await client.post("/api/v1/notes/", content=payload, headers=HEADERS)
    assert response.status_code == 422
