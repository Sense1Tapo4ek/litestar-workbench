from dataclasses import dataclass

from litestar import Litestar, Request, get
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)

from logger_setup import logger


@dataclass
class User:
    id: int
    name: str
    role: str


@dataclass
class Token:
    value: str


# Simple token -> user mapping (in-memory "database")
TOKEN_DB: dict[str, User] = {
    "token-alice": User(id=1, name="Alice", role="admin"),
    "token-bob": User(id=2, name="Bob", role="viewer"),
}


class TokenAuthMiddleware(AbstractAuthenticationMiddleware):
    exclude = ["/public", "/schema"]

    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        auth_header = connection.headers.get("authorization", "")
        logger.info(f"auth: checking token | header={'present' if auth_header else 'missing'}")

        if not auth_header.startswith("Bearer "):
            raise NotAuthorizedException(detail="Missing or invalid Authorization header")

        token_value = auth_header.removeprefix("Bearer ").strip()
        user = TOKEN_DB.get(token_value)

        if not user:
            raise NotAuthorizedException(detail="Unknown token")

        logger.info(f"auth: user={user.name}, role={user.role}")
        return AuthenticationResult(user=user, auth=Token(value=token_value))


@get("/public")
async def public_info() -> dict[str, str]:
    logger.info("handler: public_info")
    return {"info": "This is public -- no auth needed"}


@get("/me")
async def get_current_user(request: Request[User, Token, ...]) -> dict[str, str | int]:
    logger.info(f"handler: get_current_user | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name, "role": request.user.role}


@get("/admin")
async def admin_area(request: Request[User, Token, ...]) -> dict[str, str]:
    if request.user.role != "admin":
        raise NotAuthorizedException(detail="Admin access required")
    logger.info(f"handler: admin_area | user={request.user.name}")
    return {"message": f"Welcome, admin {request.user.name}!"}


app = Litestar(
    route_handlers=[public_info, get_current_user, admin_area],
    middleware=[TokenAuthMiddleware],
)
