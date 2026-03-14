from litestar import Litestar, get

from config import settings
from logger_setup import logger


@get("/config")
async def get_config() -> dict:
    logger.info(f"get_config: app={settings.app_name} debug={settings.debug}")
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "max_items": settings.max_items,
        "database_url": settings.database_url,
        # Никогда не возвращай secret_key клиенту!
    }


@get("/items")
async def list_items() -> dict:
    items = [{"id": i} for i in range(min(5, settings.max_items))]
    logger.info(f"list_items: max_items={settings.max_items} returning {len(items)}")
    return {"items": items, "limit": settings.max_items}


@get("/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


app = Litestar(
    route_handlers=[get_config, list_items, health],
    debug=settings.debug,
)
