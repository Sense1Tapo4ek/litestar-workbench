from litestar import Litestar, get
from litestar.types import ASGIApp, Receive, Scope, Send

from logger_setup import logger


def logging_middleware_factory(app: ASGIApp) -> ASGIApp:
    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            logger.info(f"middleware-1: before | path={scope['path']}")
        await app(scope, receive, send)
        if scope["type"] == "http":
            logger.info("middleware-1: after")

    return middleware


def header_middleware_factory(app: ASGIApp) -> ASGIApp:
    async def middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            logger.info("middleware-2: before")
        await app(scope, receive, send)
        if scope["type"] == "http":
            logger.info("middleware-2: after")

    return middleware


@get("/")
async def index() -> dict[str, str]:
    logger.info("handler: index")
    return {"message": "Hello, Middleware!"}


@get("/health")
async def health() -> dict[str, str]:
    logger.info("handler: health")
    return {"status": "ok"}


app = Litestar(
    route_handlers=[index, health],
    middleware=[logging_middleware_factory, header_middleware_factory],
)
