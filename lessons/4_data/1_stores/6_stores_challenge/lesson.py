import asyncio

from litestar import Litestar, get, post

# TODO: добавь необходимые импорты:
# from litestar.config.response_cache import ResponseCacheConfig
# from litestar.middleware.rate_limit import RateLimitConfig
# from litestar.stores.memory import MemoryStore
from logger_setup import logger

_call_count = 0


# TODO: добавь кэширование с TTL 10 секунд на GET /report
# Подсказка: используй декоратор cache=10 на хендлере
# и ResponseCacheConfig(store="response_cache") на уровне app
@get("/report")
async def get_report() -> dict:
    global _call_count
    _call_count += 1
    await asyncio.sleep(0.05)
    logger.info(f"get_report: computing (call #{_call_count})")
    return {"data": "expensive", "computed_at_call": _call_count}


@get("/calls")
async def call_count() -> dict:
    return {"count": _call_count}


# TODO: добавь rate limiting: не более 3 запросов в минуту на POST /items
# Подсказка: RateLimitConfig(rate_limit=("minute", 3), store="rate_limit")
@post("/items")
async def create_item(data: dict[str, str]) -> dict:
    logger.info(f"create_item: {data}")
    return {"id": 1, **data}


# TODO: добавь в Litestar:
#   1. stores={"response_cache": MemoryStore(), "rate_limit": MemoryStore()}
#   2. response_cache_config=ResponseCacheConfig(store="response_cache")
#   3. middleware=[RateLimitConfig(rate_limit=("minute", 3), store="rate_limit").middleware]
app = Litestar(
    route_handlers=[get_report, call_count, create_item],
)
