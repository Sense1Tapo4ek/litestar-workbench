from dataclasses import dataclass
from typing import Any

from litestar import Litestar, Request, Response, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTAuth, Token
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@dataclass
class User:
    id: int
    name: str
    role: str


USERS_DB: dict[str, User] = {
    "alice": User(id=1, name="Alice", role="admin"),
    "bob": User(id=2, name="Bob", role="viewer"),
}


@dataclass
class LoginRequest:
    username: str
    password: str


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    user = USERS_DB.get(token.sub)
    logger.info(f"auth: retrieve sub={token.sub} | found={user is not None}")
    return user


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret="s1t-lesson-secret-key-change-in-production",
    # Метод 1: exclude по URL-патерну (всегда открыт)
    exclude=["/login", "/public", "/schema"],
    # Метод 2: exclude_opt_key — проверяет opt метаданные хендлера
    exclude_opt_key="exclude_from_auth",
)


# Метод 1: исключён через exclude=[...] в JWTAuth
@get("/public")
async def public_info() -> dict[str, str]:
    logger.info("handler: public_info (no auth)")
    return {"message": "Public endpoint — no auth needed"}


# Метод 2: исключён через exclude_opt_key на конкретном хендлере
@get("/status", opt={"exclude_from_auth": True})
async def status() -> dict[str, str]:
    logger.info("handler: status (excluded via opt)")
    return {"status": "running", "auth": "not required"}


@post("/login", status_code=HTTP_201_CREATED)
async def login(data: LoginRequest) -> Response[dict[str, str]]:
    user = USERS_DB.get(data.username)
    if not user or data.username not in ("alice", "bob"):
        logger.warning(f"login: failed for username={data.username}")
        raise NotAuthorizedException("Invalid credentials")
    logger.info(f"login: user={data.username}")
    # JWTAuth.login() без response_body возвращает {"token": "<jwt>"} в теле
    return jwt_auth.login(identifier=data.username)


@get("/me")
async def get_me(request: Request[User, Token, Any]) -> dict[str, str | int]:
    logger.info(f"handler: get_me | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name, "role": request.user.role}


app = Litestar(
    route_handlers=[public_info, status, login, get_me],
    on_app_init=[jwt_auth.on_app_init],
)
