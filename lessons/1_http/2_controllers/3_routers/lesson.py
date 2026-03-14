from litestar import Litestar, get, post
from litestar.router import Router
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


_items: dict[int, dict] = {}
_users: dict[int, dict] = {}
_item_id = 0
_user_id = 0


@get("/")
async def list_items() -> list[dict]:
    logger.info(f"list_items: {len(_items)}")
    return list(_items.values())


@post("/", status_code=HTTP_201_CREATED)
async def create_item(data: dict) -> dict:
    global _item_id
    _item_id += 1
    item = {"id": _item_id, **data}
    _items[_item_id] = item
    logger.info(f"create_item: {_item_id}")
    return item


@get("/")
async def list_users() -> list[dict]:
    logger.info(f"list_users: {len(_users)}")
    return list(_users.values())


@post("/", status_code=HTTP_201_CREATED)
async def create_user(data: dict) -> dict:
    global _user_id
    _user_id += 1
    user = {"id": _user_id, **data}
    _users[_user_id] = user
    logger.info(f"create_user: {_user_id}")
    return user


items_router = Router(path="/items", route_handlers=[list_items, create_item])
users_router = Router(path="/users", route_handlers=[list_users, create_user])

api_router = Router(path="/api", route_handlers=[items_router, users_router])

app = Litestar(route_handlers=[api_router])
