from abc import ABC, abstractmethod

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import (
    FromDishka,
    LitestarProvider,
    inject,
    setup_dishka,
)
from litestar import Litestar, get
import logger_setup


class Greeter(ABC):
    @abstractmethod
    def greet(self, name: str) -> str: ...


class FormalGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"Good day, {name}. (formal)"


class CasualGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"Hey, {name}! (casual/mock)"


class ProdProvider(Provider):
    greeter = provide(FormalGreeter, provides=Greeter, scope=Scope.REQUEST)


class TestProvider(Provider):
    greeter = provide(
        CasualGreeter, provides=Greeter, scope=Scope.REQUEST, override=True
    )


@get("/greet/{name:str}")
@inject
async def greet(name: str, greeter: FromDishka[Greeter]) -> dict:
    return {"message": greeter.greet(name)}


@get("/impl")
@inject
async def get_impl(greeter: FromDishka[Greeter]) -> dict:
    return {"implementation": type(greeter).__name__}


# TestProvider.override=True — CasualGreeter заменяет FormalGreeter
container = make_async_container(ProdProvider(), TestProvider(), LitestarProvider())
app = Litestar(route_handlers=[greet, get_impl])
setup_dishka(container=container, app=app)
