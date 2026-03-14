from dataclasses import dataclass

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import (
    FromDishka,
    LitestarProvider,
    inject,
    setup_dishka,
)
from litestar import Litestar, get
import logger_setup


@dataclass
class Settings:
    app_name: str = "demo"
    max_items: int = 100


class Cache:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def size(self) -> int:
        return len(self._data)


@dataclass
class ItemService:
    settings: Settings
    cache: Cache

    def get_item(self, key: str) -> dict:
        cached = self.cache.get(key)
        if cached:
            return {"key": key, "value": cached, "from_cache": True}
        value = f"item-{key}"
        self.cache.set(key, value)
        return {"key": key, "value": value, "from_cache": False}

    def stats(self) -> dict:
        return {"app": self.settings.app_name, "cache_size": self.cache.size()}


class InfraProvider(Provider):
    scope = Scope.APP

    @provide
    def get_settings(self) -> Settings:
        return Settings()

    cache = provide(Cache)


class ServiceProvider(Provider):
    scope = Scope.REQUEST
    item_service = provide(ItemService)


@get("/items/{key:str}")
@inject
async def get_item(key: str, svc: FromDishka[ItemService]) -> dict:
    return svc.get_item(key)


@get("/stats")
@inject
async def stats(svc: FromDishka[ItemService]) -> dict:
    return svc.stats()


container = make_async_container(InfraProvider(), ServiceProvider(), LitestarProvider())
app = Litestar(route_handlers=[get_item, stats])
setup_dishka(container=container, app=app)
