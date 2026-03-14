from litestar import Litestar, get, post
from litestar.dto import DTOConfig, MsgspecDTO
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED

from models import User, _store, make_user
import logger_setup


class UserReadDTO(MsgspecDTO[User]):
    config = DTOConfig(exclude={"password"})


@post("/users", return_dto=UserReadDTO, status_code=HTTP_201_CREATED)
async def create_user(data: User) -> User:
    logger_setup.logger.info(f"create_user: {data.username}")
    return make_user(
        username=data.username,
        email=data.email,
        password=data.password,
    )


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
