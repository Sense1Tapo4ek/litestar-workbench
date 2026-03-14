from dataclasses import dataclass

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import (
    FromDishka,
    LitestarProvider,
    inject,
    setup_dishka,
)
from litestar import Litestar, get

from logger_setup import logger


@dataclass
class AppConfig:
    version: str = "1.0"
    debug: bool = False


@dataclass
class GreetService:
    config: AppConfig

    def greet(self) -> str:
        return f"Hello from v{self.config.version} (debug={self.config.debug})"


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def config(self) -> AppConfig:
        return AppConfig()


class ServiceProvider(Provider):
    scope = Scope.REQUEST
    greet_service = provide(GreetService)


@get("/ping")
async def ping() -> dict:
    logger.info("ping")
    return {"pong": True}


@get("/hello")
@inject
async def hello(svc: FromDishka[GreetService]) -> dict:
    return {"message": svc.greet()}


@get("/config")
@inject
async def read_config(config: FromDishka[AppConfig]) -> dict:
    return {"version": config.version, "debug": config.debug}


container = make_async_container(AppProvider(), ServiceProvider(), LitestarProvider())
app = Litestar(route_handlers=[ping, hello, read_config])
setup_dishka(container=container, app=app)
