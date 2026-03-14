import time
import uuid

from litestar import Litestar, get
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import AbstractMiddleware, DefineMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send

from logger_setup import logger


class ProcessTimeMiddleware(AbstractMiddleware):
    scopes = {ScopeType.HTTP}
    exclude = ["health"]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = time.monotonic()
        logger.info(f"process-time: start | path={scope['path']}")

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed = f"{(time.monotonic() - start) * 1000:.2f}ms"
                headers = MutableScopeHeaders.from_message(message)
                headers["X-Process-Time"] = elapsed
                logger.info(f"process-time: {elapsed}")
            await send(message)

        await self.app(scope, receive, send_with_header)


class RequestIdMiddleware(AbstractMiddleware):
    scopes = {ScopeType.HTTP}

    def __init__(self, app: ASGIApp, prefix: str = "req") -> None:
        super().__init__(app)
        self.prefix = prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request_id = f"{self.prefix}-{uuid.uuid4().hex[:8]}"
        logger.info(f"request-id: {request_id}")

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableScopeHeaders.from_message(message)
                headers["X-Request-Id"] = request_id
            await send(message)

        await self.app(scope, receive, send_with_id)


@get("/")
async def index() -> dict[str, str]:
    logger.info("handler: index")
    return {"message": "Hello, Custom Middleware!"}


@get("/health")
async def health() -> dict[str, str]:
    logger.info("handler: health")
    return {"status": "ok"}


app = Litestar(
    route_handlers=[index, health],
    middleware=[ProcessTimeMiddleware, DefineMiddleware(RequestIdMiddleware, prefix="s1t")],
)
