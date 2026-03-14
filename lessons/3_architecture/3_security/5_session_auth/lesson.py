from dataclasses import dataclass
from typing import Any

from litestar import Litestar, Request, get, post
from litestar.connection import ASGIConnection
from litestar.middleware.session.server_side import (
    ServerSideSessionBackend,
    ServerSideSessionConfig,
)
from litestar.security.session_auth import SessionAuth
from litestar.status_codes import HTTP_201_CREATED
from litestar.stores.memory import MemoryStore

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


async def retrieve_user_handler(
    session: dict[str, Any], connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = USERS_DB.get(user_id)
    logger.info(f"auth: retrieve user_id={user_id} | found={user is not None}")
    return user


@get("/public")
async def public_info() -> dict[str, str]:
    logger.info("handler: public_info")
    return {"info": "This endpoint is public -- no auth needed"}


@post("/login", status_code=HTTP_201_CREATED)
async def login(request: Request, data: dict[str, str]) -> dict[str, str]:
    username = data.get("username", "")
    user = USERS_DB.get(username)
    if not user:
        logger.warning(f"login: unknown user={username}")
        from litestar.exceptions import NotAuthorizedException

        raise NotAuthorizedException(detail="Unknown user")

    request.set_session({"user_id": username})
    logger.info(f"login: user={username}, role={user.role}")
    return {"message": f"Logged in as {username}", "role": user.role}


@get("/me")
async def get_me(request: Request[User, Any, Any]) -> dict[str, str | int]:
    logger.info(f"handler: get_me | user={request.user.name}")
    return {"id": request.user.id, "name": request.user.name, "role": request.user.role}


@post("/logout", status_code=200)
async def logout(request: Request) -> dict[str, str]:
    request.clear_session()
    logger.info("handler: logout")
    return {"message": "Logged out"}


session_auth = SessionAuth[User, ServerSideSessionBackend](
    retrieve_user_handler=retrieve_user_handler,
    session_backend_config=ServerSideSessionConfig(),
    exclude=["/login", "/public", "/schema"],
)

app = Litestar(
    route_handlers=[public_info, login, get_me, logout],
    on_app_init=[session_auth.on_app_init],
    stores={"sessions": MemoryStore()},
)
