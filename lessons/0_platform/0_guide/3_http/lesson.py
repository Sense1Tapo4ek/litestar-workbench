from litestar import Litestar, get, post
from litestar.connection import Request

from logger_setup import logger


@get("/headers")
async def read_headers(request: Request) -> dict:
    logger.info(f"read_headers: {len(request.headers)} headers")
    return {"headers": dict(request.headers)}


@get("/cookies")
async def read_cookies(request: Request) -> dict:
    logger.info(f"read_cookies: {list(request.cookies.keys())}")
    return {"cookies": dict(request.cookies)}


@post("/echo")
async def echo_body(data: dict) -> dict:
    logger.info(f"echo_body: {list(data.keys())}")
    return {"received": data}


app = Litestar([read_headers, read_cookies, echo_body])
