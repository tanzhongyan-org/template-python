"""Request identity."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings


def get_owner_id(x_user_id: Annotated[str | None, Header()] = None) -> str:
    """Return the caller's owner ID, or reject the request with 401.

    The header is honoured only when TRUST_IDENTITY_HEADER is true. A missing or
    blank header never falls back to a shared identity.

    TEMPLATE-TODO(auth): replace header identity with real authentication
    """
    owner_id = x_user_id.strip() if x_user_id else ""
    if not settings.trust_identity_header or not owner_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return owner_id


OwnerId = Annotated[str, Depends(get_owner_id)]
