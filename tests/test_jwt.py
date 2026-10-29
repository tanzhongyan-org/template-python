"""JWT bearer validation against the product JWKS."""

import time
from types import SimpleNamespace
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from httpx import AsyncClient

import app.core.jwt as jwt_module
from app.core.config import settings
from app.core.jwt import token_owner_id, validate_token

ISSUER = "https://auth.test"
AUDIENCE = "https://api.test"
JWKS_URL = "https://auth.test/api/auth/jwks"


@pytest.fixture
def signing_key() -> rsa.RSAPrivateKey:
    """Generate a fresh RSA key pair for signing test tokens."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def configured_jwt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Point the JWT settings at the test issuer."""
    monkeypatch.setattr(settings, "jwks_url", JWKS_URL)
    monkeypatch.setattr(settings, "jwt_issuer", ISSUER)
    monkeypatch.setattr(settings, "jwt_audience", AUDIENCE)


@pytest.fixture
def jwks_client(
    monkeypatch: pytest.MonkeyPatch, signing_key: rsa.RSAPrivateKey
) -> rsa.RSAPrivateKey:
    """Serve the test public key from the JWKS client instead of the network."""
    public_pem = signing_key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    fake = SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=public_pem))
    monkeypatch.setattr(jwt_module, "_get_client", lambda: fake)
    return signing_key


def make_token(key: rsa.RSAPrivateKey, **claims: Any) -> str:
    """Sign a test token with the default issuer, audience and expiry."""
    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    payload = {"iss": ISSUER, "aud": AUDIENCE, "exp": int(time.time()) + 3600}
    payload.update(claims)
    return jwt.encode(payload, private_pem, algorithm="RS256")


def test_valid_token_returns_claims(configured_jwt: None, jwks_client: rsa.RSAPrivateKey) -> None:
    claims = validate_token(make_token(jwks_client, sub="owner-jwt"))
    assert claims["sub"] == "owner-jwt"


def test_owner_id_comes_from_subject(configured_jwt: None, jwks_client: rsa.RSAPrivateKey) -> None:
    assert token_owner_id(make_token(jwks_client, sub="owner-jwt")) == "owner-jwt"


def test_missing_subject_returns_401(configured_jwt: None, jwks_client: rsa.RSAPrivateKey) -> None:
    with pytest.raises(HTTPException) as exc:
        token_owner_id(make_token(jwks_client))
    assert exc.value.status_code == 401


@pytest.mark.parametrize(
    "claims",
    [
        {"exp": int(time.time()) - 10},
        {"aud": "https://other.test"},
        {"iss": "https://other.test"},
    ],
)
def test_bad_claims_return_401(
    configured_jwt: None, jwks_client: rsa.RSAPrivateKey, claims: dict[str, Any]
) -> None:
    with pytest.raises(HTTPException) as exc:
        validate_token(make_token(jwks_client, sub="owner-jwt", **claims))
    assert exc.value.status_code == 401


def test_wrong_key_returns_401(configured_jwt: None, jwks_client: rsa.RSAPrivateKey) -> None:
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(HTTPException) as exc:
        validate_token(make_token(other, sub="owner-jwt"))
    assert exc.value.status_code == 401


def test_unconfigured_jwks_rejects_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "jwks_url", None)
    with pytest.raises(HTTPException) as exc:
        validate_token("anything")
    assert exc.value.status_code == 401


async def test_bearer_creates_notes_as_subject(
    client: AsyncClient,
    configured_jwt: None,
    jwks_client: rsa.RSAPrivateKey,
) -> None:
    headers = {"Authorization": f"Bearer {make_token(jwks_client, sub='owner-jwt-1')}"}
    created = await client.post("/api/v1/notes/", json={"title": "t", "body": "b"}, headers=headers)
    assert created.status_code == 201
    assert created.json()["owner_id"] == "owner-jwt-1"

    other = {"Authorization": f"Bearer {make_token(jwks_client, sub='owner-jwt-2')}"}
    missing = await client.get(f"/api/v1/notes/{created.json()['id']}", headers=other)
    assert missing.status_code == 404


async def test_bearer_wins_over_dev_header(
    client: AsyncClient,
    configured_jwt: None,
    jwks_client: rsa.RSAPrivateKey,
) -> None:
    headers = {
        "Authorization": f"Bearer {make_token(jwks_client, sub='owner-jwt-3')}",
        "x-user-id": "owner-header",
    }
    created = await client.post("/api/v1/notes/", json={"title": "t", "body": "b"}, headers=headers)
    assert created.status_code == 201
    assert created.json()["owner_id"] == "owner-jwt-3"


async def test_malformed_authorization_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/notes/", headers={"Authorization": "Bearer"})
    assert response.status_code == 401
