from dataclasses import dataclass
from datetime import timedelta

from litestar import Litestar, Request, delete, get, post
from litestar.status_codes import HTTP_201_CREATED
from litestar.stores.memory import MemoryStore

from logger_setup import logger


@dataclass
class SetRequest:
    key: str
    value: str
    ttl: int = 60


@get("/store/info")
async def store_info(request: Request) -> dict:
    store = request.app.stores.get("main")
    return {"store_type": type(store).__name__, "store_name": "main"}


@post("/store/set", status_code=HTTP_201_CREATED)
async def store_set(request: Request, data: SetRequest) -> dict:
    store = request.app.stores.get("main")
    await store.set(
        data.key, data.value.encode(), expires_in=timedelta(seconds=data.ttl)
    )
    logger.info(f"SET {data.key} TTL={data.ttl}s")
    return {"key": data.key, "ttl_seconds": data.ttl}


@get("/store/get/{key:str}")
async def store_get(request: Request, key: str) -> dict:
    store = request.app.stores.get("main")
    raw = await store.get(key)
    logger.info(f"GET {key} → {'HIT' if raw else 'MISS'}")
    return {"key": key, "value": raw.decode() if raw else None}


@get("/store/exists/{key:str}")
async def store_exists(request: Request, key: str) -> dict:
    store = request.app.stores.get("main")
    exists = await store.exists(key)
    return {"key": key, "exists": exists}


@delete("/store/del/{key:str}")
async def store_delete(request: Request, key: str) -> None:
    store = request.app.stores.get("main")
    await store.delete(key)
    logger.info(f"DEL {key}")


app = Litestar(
    route_handlers=[store_info, store_set, store_get, store_exists, store_delete],
    stores={"main": MemoryStore()},
)
