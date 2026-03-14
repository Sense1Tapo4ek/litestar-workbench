from litestar import Litestar, get

from logger_setup import logger


@get("/")
async def index() -> dict:
    logger.info("index")
    return {"message": "Hello from Litestar!", "version": "2.x"}


@get("/health")
async def health() -> dict:
    logger.info("health")
    return {"status": "ok"}


app = Litestar(route_handlers=[index, health])
