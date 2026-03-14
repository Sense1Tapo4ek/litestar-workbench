from dataclasses import dataclass

from litestar import Litestar, delete, get, post
from litestar.router import Router
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from logger_setup import logger


@dataclass
class Item:
    id: int | None
    name: str


_store: dict[int, Item] = {}
_next_id = 1


@get("/")
async def list_items() -> list[Item]:
    logger.info(f"list_items: {len(_store)}")
    return list(_store.values())


@post("/", status_code=HTTP_201_CREATED)
async def create_item(data: Item) -> Item:
    global _next_id
    item = Item(id=_next_id, name=data.name)
    _store[_next_id] = item
    _next_id += 1
    logger.info(f"create_item: {item.id} {item.name!r}")
    return item


@get("/{item_id:int}")
async def get_item(item_id: int) -> Item | None:
    logger.info(f"get_item: {item_id}")
    return _store.get(item_id)


@delete("/{item_id:int}", status_code=HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    logger.info(f"delete_item: {item_id}")
    _store.pop(item_id, None)


items_router = Router(
    path="/items", route_handlers=[list_items, create_item, get_item, delete_item]
)

app = Litestar(route_handlers=[items_router])
