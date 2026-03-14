from litestar import Litestar, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException
from litestar.handlers import BaseRouteHandler

import logger_setup

VALID_API_KEY = "challenge-key-2024"

_items: list[dict[str, str | int]] = [
    {"id": 1, "name": "Item A"},
    {"id": 2, "name": "Item B"},
]
_counter = 2


# TODO: реализуй guard api_key_guard
# Проверяет заголовок "x-api-key". Если отсутствует или не равен VALID_API_KEY -> NotAuthorizedException
def api_key_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    pass


# TODO: реализуй guard admin_guard
# Проверяет заголовок "x-role". Если не равен "admin" -> PermissionDeniedException
def admin_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    pass


@get("/items")
async def list_items() -> list[dict[str, str | int]]:
    return _items


# TODO: добавь guards=[api_key_guard] к этому хендлеру
@post("/items")
async def create_item(data: dict[str, str]) -> dict[str, str | int]:
    global _counter
    _counter += 1
    item = {"id": _counter, **data}
    _items.append(item)
    return item


# TODO: добавь guards=[api_key_guard, admin_guard] к этому хендлеру
@get("/admin/stats")
async def admin_stats() -> dict[str, int]:
    return {"total_items": len(_items)}


app = Litestar(route_handlers=[list_items, create_item, admin_stats])
