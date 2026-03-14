from litestar import Litestar, get, post
from litestar.dto import DataclassDTO, DTOConfig, DTOData
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED

from models import User, _store, next_id
import logger_setup


class UserWriteDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"id", "created_at", "role"})


class UserReadDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"password"})


@post("/users", dto=UserWriteDTO, return_dto=UserReadDTO, status_code=HTTP_201_CREATED)
async def create_user(data: DTOData[User]) -> User:
    user = data.create_instance(id=next_id(), role="user")
    logger_setup.logger.info(f"create_user: {user.id}")
    _store[user.id] = user
    return user


@get("/users", return_dto=UserReadDTO)
async def list_users() -> list[User]:
    logger_setup.logger.info(f"list_users: {len(_store)}")
    return list(_store.values())


@get("/users/{user_id:int}", return_dto=UserReadDTO)
async def get_user(user_id: int) -> User:
    logger_setup.logger.info(f"get_user: {user_id}")
    user = _store.get(user_id)
    if user is None:
        raise NotFoundException(f"User {user_id} not found")
    return user


app = Litestar(route_handlers=[create_user, list_users, get_user])
