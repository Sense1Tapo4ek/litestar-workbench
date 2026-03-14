from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import (
    FromDishka,
    LitestarProvider,
    inject_websocket,
    setup_dishka,
)
from litestar import Litestar, websocket_listener
import logger_setup


class MessageLog:
    """SESSION scope — один экземпляр на протяжении всего WebSocket-соединения."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def add(self, msg: str) -> None:
        self.messages.append(msg)

    def count(self) -> int:
        return len(self.messages)


class SessionProvider(Provider):
    log = provide(MessageLog, scope=Scope.SESSION)


@websocket_listener("/ws")
@inject_websocket
async def ws_echo(data: str, log: FromDishka[MessageLog]) -> str:
    log.add(data)
    return f"msg#{log.count()}:{data}"


container = make_async_container(SessionProvider(), LitestarProvider())
app = Litestar(route_handlers=[ws_echo])
setup_dishka(container=container, app=app)
