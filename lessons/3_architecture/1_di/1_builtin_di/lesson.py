from collections.abc import Generator
from typing import Annotated

from litestar import Litestar, get
from litestar.di import Provide
from litestar.params import Dependency

from logger_setup import logger


async def provide_db_url() -> str:
    return "sqlite:///demo.db"


async def provide_db_info(db_url: str) -> dict:
    return {"url": db_url, "engine": "sqlite"}


def provide_connection() -> Generator[dict, None, None]:
    conn = {"status": "open", "id": 42}
    try:
        yield conn
    finally:
        conn["status"] = "closed"


async def provide_raw() -> str:
    return "i-am-a-string"


@get("/url")
async def get_url(db_url: str) -> dict:
    logger.info(f"get_url: {db_url}")
    return {"db_url": db_url}


@get("/chain")
async def get_chain(db_info: dict) -> dict:
    logger.info(f"get_chain: {db_info}")
    return db_info


@get("/connection")
async def get_conn(conn: dict) -> dict:
    logger.info(f"get_conn: status={conn['status']}")
    return {"status": conn["status"], "id": conn["id"]}


@get("/skip")
async def get_skip(
    raw: Annotated[int, Dependency(skip_validation=True)],
) -> dict:
    logger.info(f"get_skip: raw={raw!r} type={type(raw).__name__}")
    return {"value": raw, "type": type(raw).__name__}


app = Litestar(
    route_handlers=[get_url, get_chain, get_conn, get_skip],
    dependencies={
        "db_url": Provide(provide_db_url),
        "db_info": Provide(provide_db_info),
        "conn": Provide(provide_connection),
        "raw": Provide(provide_raw),
    },
)
