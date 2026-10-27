"""Integration tests for notes endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_note_round_trip(client: AsyncClient) -> None:
    headers = {"x-user-id": "owner-1"}
    create_res = await client.post(
        "/api/v1/notes/",
        json={"title": "Test Note", "body": "My body content"},
        headers=headers,
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["title"] == "Test Note"
    assert data["body"] == "My body content"
    note_id = data["id"]

    get_res = await client.get(f"/api/v1/notes/{note_id}", headers=headers)
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["id"] == note_id
    assert fetched["title"] == "Test Note"


@pytest.mark.asyncio
async def test_validation_rejects_bad_input(client: AsyncClient) -> None:
    headers = {"x-user-id": "owner-val"}
    # Empty title (<1 char)
    res_empty = await client.post(
        "/api/v1/notes/",
        json={"title": "", "body": "empty"},
        headers=headers,
    )
    assert res_empty.status_code == 422

    # Title too long (>200 chars)
    res_long = await client.post(
        "/api/v1/notes/",
        json={"title": "x" * 201, "body": "too long"},
        headers=headers,
    )
    assert res_long.status_code == 422


@pytest.mark.asyncio
async def test_tenant_isolation_owner_a_vs_b(client: AsyncClient) -> None:
    alice_headers = {"x-user-id": "owner-alice"}
    bob_headers = {"x-user-id": "owner-bob"}

    # Alice creates a note
    res = await client.post(
        "/api/v1/notes/",
        json={"title": "Alice Secret", "body": "Top secret"},
        headers=alice_headers,
    )
    assert res.status_code == 201
    note_id = res.json()["id"]

    # Bob cannot read Alice's note
    bob_get = await client.get(f"/api/v1/notes/{note_id}", headers=bob_headers)
    assert bob_get.status_code == 404

    # Bob cannot update Alice's note
    bob_patch = await client.patch(
        f"/api/v1/notes/{note_id}",
        json={"title": "Bob Tamper"},
        headers=bob_headers,
    )
    assert bob_patch.status_code == 404

    # Bob cannot delete Alice's note
    bob_delete = await client.delete(f"/api/v1/notes/{note_id}", headers=bob_headers)
    assert bob_delete.status_code == 404

    # Alice can delete her note
    alice_delete = await client.delete(f"/api/v1/notes/{note_id}", headers=alice_headers)
    assert alice_delete.status_code == 204

    # Post-delete Alice cannot read it
    alice_get = await client.get(f"/api/v1/notes/{note_id}", headers=alice_headers)
    assert alice_get.status_code == 404
