from litestar import Litestar, get, patch, post
from litestar.dto import DataclassDTO, DTOConfig, DTOData
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger
from models import Item, _store, next_id


class ItemWriteDTO(DataclassDTO[Item]):
    # BUG 1: "secret" не существует в Item — owner_id не исключается и попадает в ответ
    config = DTOConfig(exclude={"id", "created_at", "secret"})


class ItemReadDTO(DataclassDTO[Item]):
    config = DTOConfig(exclude={"owner_id"})


class ItemPatchDTO(DataclassDTO[Item]):
    # BUG 2: partial=True отсутствует — PATCH требует все поля вместо частичного обновления
    config = DTOConfig(exclude={"id", "created_at", "owner_id"})


# BUG 3: dto= и return_dto= перепутаны местами — DTO для чтения используется для входных данных
@post("/items", dto=ItemReadDTO, return_dto=ItemWriteDTO, status_code=HTTP_201_CREATED)
async def create_item(data: DTOData[Item]) -> Item:
    item = data.create_instance(id=next_id(), owner_id=0)
    logger.info(f"create_item: {item.id}")
    _store[item.id] = item
    return item


@patch("/items/{item_id:int}", dto=ItemPatchDTO, return_dto=ItemReadDTO)
async def patch_item(item_id: int, data: DTOData[Item]) -> Item:
    logger.info(f"patch_item: {item_id}")
    item = _store.get(item_id)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return data.update_instance(item)


@get("/items/{item_id:int}", return_dto=ItemReadDTO)
async def get_item(item_id: int) -> Item:
    logger.info(f"get_item: {item_id}")
    item = _store.get(item_id)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return item


app = Litestar(route_handlers=[create_item, patch_item, get_item])
