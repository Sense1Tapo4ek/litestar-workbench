from litestar import Litestar, get
from litestar.config.compression import CompressionConfig

from logger_setup import logger


@get("/small")
async def small_response() -> dict[str, str]:
    logger.info("small_response: returning small payload")
    return {"message": "short"}


@get("/large")
async def large_response() -> dict[str, list[str]]:
    items = [f"item-{i}: " + "x" * 100 for i in range(100)]
    logger.info(f"large_response: {len(items)} items, ~{sum(len(s) for s in items)} bytes")
    return {"items": items}


@get("/json-data")
async def json_data() -> list[dict[str, str | int]]:
    data = [{"id": i, "name": f"user-{i}", "email": f"user{i}@example.com"} for i in range(50)]
    logger.info(f"json_data: {len(data)} records")
    return data


app = Litestar(
    route_handlers=[small_response, large_response, json_data],
    compression_config=CompressionConfig(backend="gzip", gzip_compress_level=6, minimum_size=500),
)
