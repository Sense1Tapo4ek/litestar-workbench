from litestar import Litestar, get

from logger_setup import logger


@get("/")
async def welcome() -> dict:
    logger.info("welcome")
    return {"message": "Welcome to S1T Litestar Workbench", "ready": True}


@get("/ping")
async def ping() -> dict:
    logger.info("ping")
    return {"pong": True}


app = Litestar(route_handlers=[welcome, ping])
