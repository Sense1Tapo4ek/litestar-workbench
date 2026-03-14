from litestar import Litestar, get, post
from litestar.config.cors import CORSConfig
from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import AbstractMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send

import logger_setup


class AuthLogMiddleware(AbstractMiddleware):
    scopes = {ScopeType.HTTP}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        token = ""
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"authorization":
                token = header_value.decode()
                break
        logger_setup.logger.info(f"auth-log: token={'present' if token else 'missing'} | path={scope['path']}")
        await self.app(scope, receive, send)


class UpperCaseMiddleware(AbstractMiddleware):
    # BUG 1: scopes includes WEBSOCKET but this middleware only handles HTTP response headers
    scopes = {ScopeType.HTTP, ScopeType.WEBSOCKET}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableScopeHeaders.from_message(message)
                headers["X-Powered-By"] = "S1T"
            await send(message)

        await self.app(scope, receive, send_wrapper)


@get("/api/items")
async def list_items() -> list[dict[str, str | int]]:
    logger_setup.logger.info("handler: list_items")
    return [{"id": 1, "name": "Item A"}, {"id": 2, "name": "Item B"}]


@post("/api/items")
async def create_item(data: dict[str, str]) -> dict[str, str | int]:
    logger_setup.logger.info(f"handler: create_item | data={data}")
    return {"id": 3, **data}


# BUG 2: allow_origins=["*"] with allow_credentials=True is invalid
cors_config = CORSConfig(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
)

app = Litestar(
    route_handlers=[list_items, create_item],
    cors_config=cors_config,
    # BUG 3: AuthLogMiddleware is defined but NOT added to the middleware list
    middleware=[UpperCaseMiddleware],
)
