from dataclasses import dataclass

from litestar import Litestar, get, post
from litestar.exceptions import NotFoundException
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Tag
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@dataclass
class Item:
    id: int | None
    name: str
    price: float


_store: dict[int, Item] = {}
_next_id = 1


@get(
    "/items",
    tags=["items"],
    summary="Список элементов",
    description="Возвращает все элементы из хранилища.",
)
async def list_items() -> list[Item]:
    logger.info(f"list_items: {len(_store)}")
    return list(_store.values())


@post(
    "/items",
    tags=["items"],
    status_code=HTTP_201_CREATED,
    summary="Создать элемент",
)
async def create_item(data: Item) -> Item:
    global _next_id
    item = Item(id=_next_id, name=data.name, price=data.price)
    _store[_next_id] = item
    _next_id += 1
    logger.info(f"create_item: {item.id} {item.name!r}")
    return item


@get("/items/{item_id:int}", tags=["items"])
async def get_item(item_id: int) -> Item:
    logger.info(f"get_item: {item_id}")
    item = _store.get(item_id)
    if item is None:
        raise NotFoundException(detail=f"Item {item_id} not found")
    return item


@get("/health", include_in_schema=False)
async def health() -> dict:
    return {"status": "ok"}


app = Litestar(
    route_handlers=[list_items, create_item, get_item, health],
    openapi_config=OpenAPIConfig(
        title="Items API",
        version="1.0.0",
        description="Учебный пример Items API.",
        tags=[Tag(name="items", description="Операции с элементами")],
    ),
)
