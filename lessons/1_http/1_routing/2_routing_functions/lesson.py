from litestar import Litestar, delete, get, patch, post, put
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from models import Item, create_item, delete_item, get_item, list_items, update_item
from logger_setup import logger


@get("/items")
async def get_items() -> list[Item]:
    items = list_items()
    logger.info(f"get_items: {len(items)}")
    return items


@post("/items", status_code=HTTP_201_CREATED)
async def create_new_item(data: Item) -> Item:
    item = create_item(name=data.name, price=data.price)
    logger.info(f"create_new_item: {item.id}")
    return item


@get("/items/{item_id:int}")
async def get_one_item(item_id: int) -> Item:
    logger.info(f"get_one_item: {item_id}")
    item = get_item(item_id)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return item


@put("/items/{item_id:int}")
async def replace_item(item_id: int, data: Item) -> Item:
    logger.info(f"replace_item: {item_id}")
    item = update_item(item_id, name=data.name, price=data.price)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return item


@patch("/items/{item_id:int}")
async def patch_item(item_id: int, data: Item) -> Item:
    logger.info(f"patch_item: {item_id}")
    fields = {}
    if data.name:
        fields["name"] = data.name
    if data.price is not None:
        fields["price"] = data.price
    item = update_item(item_id, **fields)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return item


@delete("/items/{item_id:int}", status_code=HTTP_204_NO_CONTENT)
async def remove_item(item_id: int) -> None:
    logger.info(f"remove_item: {item_id}")
    if not delete_item(item_id):
        raise NotFoundException(f"Item {item_id} not found")


app = Litestar(
    route_handlers=[
        get_items,
        create_new_item,
        get_one_item,
        replace_item,
        patch_item,
        remove_item,
    ]
)
