from dataclasses import dataclass

from litestar import Litestar, Request, get, post
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.status_codes import HTTP_201_CREATED
from litestar.stores.memory import MemoryStore

from logger_setup import logger


@dataclass
class LoginRequest:
    username: str
    role: str = "user"


@get("/me")
async def me(request: Request) -> dict:
    username = request.session.get("username")
    role = request.session.get("role")
    return {"username": username, "role": role, "logged_in": username is not None}


@post("/login", status_code=HTTP_201_CREATED)
async def login(request: Request, data: LoginRequest) -> dict:
    request.session["username"] = data.username
    request.session["role"] = data.role
    logger.info(f"Login: {data.username} role={data.role}")
    return {"message": f"Logged in as {data.username}", "role": data.role}


@post("/logout")
async def logout(request: Request) -> dict:
    request.session.clear()
    logger.info("Logout: session cleared")
    return {"message": "Logged out"}


app = Litestar(
    route_handlers=[me, login, logout],
    middleware=[ServerSideSessionConfig().middleware],
    stores={"sessions": MemoryStore()},
)
