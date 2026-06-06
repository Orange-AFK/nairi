from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

from fastapi import Header, Request
from fastapi.responses import JSONResponse

ADMIN_ALL_SCOPE = "admin:all"


@dataclass(frozen=True)
class AuthenticatedActor:
    token: str
    scopes: frozenset[str]


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: dict[str, str] | None = None) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def api_error_response(_request: Request, error: Exception) -> JSONResponse:
    if not isinstance(error, ApiError):
        raise error
    return JSONResponse(
        status_code=error.status_code,
        content={
            "code": error.code,
            "message": error.message,
            "details": error.details,
            "requestId": "unavailable",
        },
    )


def parse_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise ApiError(401, "unauthorized", "Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise ApiError(401, "unauthorized", "Missing bearer token")
    return token


def require_scope(required_scope: str) -> Callable[[Request, Annotated[str | None, Header(alias="Authorization")]], AuthenticatedActor]:
    def dependency(request: Request, authorization: Annotated[str | None, Header(alias="Authorization")] = None) -> AuthenticatedActor:
        token = parse_bearer_token(authorization)
        token_scopes = request.app.state.settings.api_tokens.get(token)
        if token_scopes is None:
            raise ApiError(401, "unauthorized", "Invalid bearer token")
        scopes = frozenset(token_scopes)
        if required_scope not in scopes and ADMIN_ALL_SCOPE not in scopes:
            raise ApiError(
                403,
                "forbidden",
                "Missing required scope",
                {"requiredScope": required_scope},
            )
        return AuthenticatedActor(token=token, scopes=scopes)

    return dependency
