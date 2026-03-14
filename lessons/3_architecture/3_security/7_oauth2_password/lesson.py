from dataclasses import dataclass
from typing import Any

from litestar import Litestar, Request, Response, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.security.jwt import OAuth2Login, OAuth2PasswordBearerAuth, Token

from logger_setup import logger


@dataclass
class User:
    id: int
    name: str
    role: str


@dataclass
class LoginRequest:
    username: str
    password: str


USERS_DB: dict[str, User] = {
    "alice": User(id=1, name="Alice", role="admin"),
    "bob": User(id=2, name="Bob", role="viewer"),
}

PASSWORDS: dict[str, str] = {
    "alice": "secret-alice",
    "bob": "secret-bob",
}


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    user = USERS_DB.get(token.sub)
    logger.info(f"auth: retrieve sub={token.sub} | found={user is not None}")
    return user


oauth2_auth = OAuth2PasswordBearerAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="s1t-lesson-secret-key-change-in-production",
    token_url="/login",
    exclude=["/login", "/public", "/schema"],
)


@get("/public")
async def public_info() -> dict[str, str]:
    logger.info("handler: public_info")
    return {"info": "This endpoint is public"}


@post("/login")
async def login(data: LoginRequest) -> Response[OAuth2Login]:
    user = USERS_DB.get(data.username)
    stored_password = PASSWORDS.get(data.username)

    if not user or stored_password != data.password:
        logger.warning(f"login: failed for username={data.username}")
        raise NotAuthorizedException(detail="Invalid credentials")

    logger.info(f"login: user={data.username}, role={user.role}")
    return oauth2_auth.login(
        identifier=data.username,
        token_extras={"role": user.role},
    )


@get("/me")
async def get_me(request: Request[User, Token, Any]) -> dict[str, str | int]:
    logger.info(f"handler: get_me | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name, "role": request.user.role}


def admin_guard(connection: ASGIConnection[Any, Any, Any, Any], _: Any) -> None:
    if connection.user.role != "admin":
        logger.warning(f"guard: access denied for user={connection.user.name}")
        raise PermissionDeniedException(detail="Admin access required")


@get("/users", guards=[admin_guard])
async def list_users(request: Request[User, Token, Any]) -> list[dict[str, str | int]]:
    logger.info(f"handler: list_users | requested_by={request.user.name}")
    return [{"id": u.id, "name": u.name, "role": u.role} for u in USERS_DB.values()]


app = Litestar(
    route_handlers=[public_info, login, get_me, list_users],
    on_app_init=[oauth2_auth.on_app_init],
)
