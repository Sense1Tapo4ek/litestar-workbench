from dataclasses import dataclass
from typing import Any

from litestar import Litestar, Request, Response, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTCookieAuth, Token
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@dataclass
class User:
    id: int
    name: str


USERS_DB: dict[str, User] = {
    "alice": User(id=1, name="Alice"),
    "bob": User(id=2, name="Bob"),
}


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    # BUG 2: Looking up by token.extras["user_id"] instead of token.sub
    user_id = token.extras.get("user_id")
    user = USERS_DB.get(user_id) if user_id else None
    logger.info(f"auth: retrieve user_id={user_id} | found={user is not None}")
    return user


jwt_cookie_auth = JWTCookieAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="s1t-lesson-secret-key",
    # BUG 1: /login is NOT in exclude -- login endpoint requires auth (chicken-and-egg)
    exclude=["/items", "/schema"],
)


@get("/items")
async def list_items() -> list[dict[str, str | int]]:
    logger.info("handler: list_items")
    return [{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]


@post("/login", status_code=HTTP_201_CREATED)
async def login(data: dict[str, str]) -> Response[dict[str, str]]:
    username = data.get("username", "")
    user = USERS_DB.get(username)
    if not user:
        raise NotAuthorizedException(detail="Unknown user")

    logger.info(f"login: user={username}")
    return jwt_cookie_auth.login(
        identifier=username,
        response_body={"message": f"Welcome, {user.name}!"},
    )


@get("/me")
async def get_me(request: Request[User, Token, Any]) -> dict[str, str | int]:
    logger.info(f"handler: get_me | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name}


# BUG 3: on_app_init is not passed to Litestar -- middleware never registers
app = Litestar(
    route_handlers=[list_items, login, get_me],
)
