"""Exception handlers that keep every error body in the {"detail": ...} shape."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return 422 with the location and message of each error, without echoing input.

    Echoing the rejected input can fail to encode (lone surrogates) and can reflect
    sensitive values back to the caller.
    """
    if not isinstance(exc, RequestValidationError):
        raise exc
    detail = [
        {"type": error["type"], "loc": list(error["loc"]), "msg": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse({"detail": detail}, status_code=422)
