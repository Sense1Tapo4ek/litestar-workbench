from litestar import Litestar, Router, get
from litestar.connection import ASGIConnection
from litestar.controller import Controller
from litestar.datastructures import ResponseHeader
from litestar.di import Provide
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler
import logger_setup


def require_token(connection: ASGIConnection, handler: BaseRouteHandler) -> None:
    if not connection.headers.get("Authorization"):
        raise NotAuthorizedException("Authorization header required")


async def app_service() -> str:
    return "app"


async def router_service() -> str:
    return "router"


async def handler_service() -> str:
    return "handler"


class ItemController(Controller):
    path = "/items"
    tags = ["items"]
    dependencies = {"service": Provide(router_service)}
    response_headers = [ResponseHeader(name="X-Layer", value="controller")]

    @get("/info")
    async def info(self, service: str) -> dict:
        return {"service": service}

    @get("/custom", dependencies={"service": Provide(handler_service)})
    async def custom(self, service: str) -> dict:
        return {"service": service}

    @get("/secured", guards=[require_token])
    async def secured(self) -> dict:
        return {"ok": True}


api_router = Router(
    path="/api",
    route_handlers=[ItemController],
    response_headers=[ResponseHeader(name="X-Router", value="yes")],
)

app = Litestar(
    route_handlers=[api_router],
    dependencies={"service": Provide(app_service)},
    response_headers=[ResponseHeader(name="X-App", value="yes")],
)
