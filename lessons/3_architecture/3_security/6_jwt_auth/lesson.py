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


jwt_cookie_auth = JWTCookieAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="s1t-lesson-secret-key-change-in-production",
    exclude=["/login", "/public", "/schema"],
)


@get("/public")
async def public_info() -> dict[str, str]:
    logger.info("handler: public_info")
    return {"info": "This endpoint is public"}


@post("/login", status_code=HTTP_201_CREATED)
async def login(data: LoginRequest) -> Response[dict[str, str]]:
    user = USERS_DB.get(data.username)
    stored_password = PASSWORDS.get(data.username)

    if not user or stored_password != data.password:
        logger.warning(f"login: failed for username={data.username}")
        raise NotAuthorizedException(detail="Invalid credentials")

    logger.info(f"login: user={data.username}, role={user.role}")
    return jwt_cookie_auth.login(
        identifier=data.username,
        token_extras={"role": user.role},
        response_body={"message": f"Welcome, {user.name}!", "role": user.role},
    )


@get("/me")
async def get_me(request: Request[User, Token, Any]) -> dict[str, str | int]:
    logger.info(f"handler: get_me | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name, "role": request.user.role}


app = Litestar(
    route_handlers=[public_info, login, get_me],
    on_app_init=[jwt_cookie_auth.on_app_init],
)
