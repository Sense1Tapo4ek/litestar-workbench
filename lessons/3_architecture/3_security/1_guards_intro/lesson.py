from litestar import Litestar, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler

from logger_setup import logger


def api_key_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    api_key = connection.headers.get("x-api-key")
    logger.info(f"api_key_guard: key={'present' if api_key else 'missing'}")
    if not api_key or api_key != "secret-key-123":
        raise NotAuthorizedException(detail="Invalid or missing API key")


@get("/public")
async def public_endpoint() -> dict[str, str]:
    logger.info("public_endpoint: no guard")
    return {"message": "Public data -- no API key needed"}


@get("/protected", guards=[api_key_guard])
async def protected_endpoint() -> dict[str, str]:
    logger.info("protected_endpoint: guard passed")
    return {"message": "Secret data -- API key valid"}


@post("/protected/items", guards=[api_key_guard])
async def create_protected_item(data: dict[str, str]) -> dict[str, str | int]:
    logger.info(f"create_protected_item: {data}")
    return {"id": 1, **data}


app = Litestar(route_handlers=[public_endpoint, protected_endpoint, create_protected_item])
