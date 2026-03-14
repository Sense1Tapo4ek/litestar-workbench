from litestar import Litestar, get, patch, post
from litestar.dto import DataclassDTO, DTOConfig, DTOData
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED

from models import User, _store, next_id
import logger_setup


class UserWriteDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"id", "created_at", "role"})


class UserPatchDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"id", "created_at", "role"}, partial=True)


class UserReadDTO(DataclassDTO[User]):
    config = DTOConfig(exclude={"password"})


@post("/users", dto=UserWriteDTO, return_dto=UserReadDTO, status_code=HTTP_201_CREATED)
async def create_user(data: DTOData[User]) -> User:
    user = data.create_instance(id=next_id(), role="user")
    logger_setup.logger.info(f"create_user: {user.id}")
    _store[user.id] = user
    return user


@patch("/users/{user_id:int}", dto=UserPatchDTO, return_dto=UserReadDTO)
async def patch_user(user_id: int, data: DTOData[User]) -> User:
    logger_setup.logger.info(f"patch_user: {user_id}")
    user = _store.get(user_id)
    if user is None:
        raise NotFoundException(f"User {user_id} not found")
    return data.update_instance(user)


@get("/users/{user_id:int}", return_dto=UserReadDTO)
async def get_user(user_id: int) -> User:
    logger_setup.logger.info(f"get_user: {user_id}")
    user = _store.get(user_id)
    if user is None:
        raise NotFoundException(f"User {user_id} not found")
    return user


app = Litestar(route_handlers=[create_user, patch_user, get_user])
