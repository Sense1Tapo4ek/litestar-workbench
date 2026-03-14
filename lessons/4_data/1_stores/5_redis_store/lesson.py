import os
from dataclasses import dataclass

from litestar import Litestar, Request, get, post
from litestar.config.response_cache import ResponseCacheConfig
from litestar.status_codes import HTTP_201_CREATED
from litestar.stores.valkey import ValkeyStore
from litestar.stores.registry import StoreRegistry

from logger_setup import logger

VALKEY_URL = os.environ.get("S1T_VALKEY_URL", "valkey://localhost:6379")

root_store = ValkeyStore.with_client(url=VALKEY_URL)

stores = StoreRegistry(
    stores={
        "response_cache": root_store.with_namespace("response_cache"),
        "kv": root_store.with_namespace("kv"),
    },
    default_factory=root_store.with_namespace,
)

_compute_calls = 0


@dataclass
class KVPayload:
    value: str


@get("/kv/{key:str}")
async def kv_get(request: Request, key: str) -> dict:
    store = request.app.stores.get("kv")
    raw = await store.get(key)
    logger.info(f"Redis GET {key} → {'HIT' if raw else 'MISS'}")
    return {"key": key, "value": raw.decode() if raw else None}


@post("/kv/{key:str}", status_code=HTTP_201_CREATED)
async def kv_set(request: Request, key: str, data: KVPayload) -> dict:
    store = request.app.stores.get("kv")
    await store.set(key, data.value.encode())
    logger.info(f"Redis SET {key}")
    return {"key": key, "stored": True}


@get("/cached", cache=True)
async def cached_handler() -> dict:
    global _compute_calls
    _compute_calls += 1
    logger.info(f"cached_handler() executed (count={_compute_calls})")
    return {"data": "expensive result", "compute_count": _compute_calls}


app = Litestar(
    route_handlers=[kv_get, kv_set, cached_handler],
    stores=stores,
    response_cache_config=ResponseCacheConfig(store="response_cache"),
)
