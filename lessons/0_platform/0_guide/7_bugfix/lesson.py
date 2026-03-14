from litestar import Litestar, get, post
import logger_setup


@get("/ping")
async def ping() -> dict:
    return {"pong": True}


@post("/items")
async def list_items() -> list:
    return ["apple", "banana", "cherry"]


@get("/health")
async def health() -> dict:
    return {"status": "ok"}


app = Litestar(route_handlers=[ping, list_items])
