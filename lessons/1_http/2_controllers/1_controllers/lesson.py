from litestar import Controller, Litestar, delete, get, post
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from models import Item, create_item, delete_item, get_item, list_items
from logger_setup import logger


class ItemController(Controller):
    path = "/items"
    tags = ["items"]

    @get()
    async def get_items(self) -> list[Item]:
        items = list_items()
        logger.info(f"get_items: {len(items)}")
        return items

    @post(status_code=HTTP_201_CREATED)
    async def create_item(self, data: Item) -> Item:
        item = create_item(name=data.name, price=data.price)
        logger.info(f"create_item: {item.id} {item.name!r}")
        return item

    @get("/{item_id:int}")
    async def get_item(self, item_id: int) -> Item:
        logger.info(f"get_item: {item_id}")
        item = get_item(item_id)
        if item is None:
            raise NotFoundException(f"Item {item_id} not found")
        return item

    @delete("/{item_id:int}", status_code=HTTP_204_NO_CONTENT)
    async def delete_item(self, item_id: int) -> None:
        logger.info(f"delete_item: {item_id}")
        if not delete_item(item_id):
            raise NotFoundException(f"Item {item_id} not found")


app = Litestar(route_handlers=[ItemController])
