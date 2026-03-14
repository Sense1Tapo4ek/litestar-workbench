from dataclasses import dataclass

from litestar import Litestar, get
from litestar.enums import MediaType
from litestar.response import Redirect, Response
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@dataclass
class Item:
    id: int
    name: str


@get("/json")
async def get_json() -> Item:
    logger.info("get_json")
    return Item(id=1, name="Litestar")


@get("/text", media_type=MediaType.TEXT)
async def get_text() -> str:
    return "Hello, World!"


@get("/html", media_type=MediaType.HTML)
async def get_html() -> str:
    return "<h1>Hello from Litestar</h1>"


@get("/redirect")
async def get_redirect() -> Redirect:
    logger.info("get_redirect → /json")
    return Redirect(path="/json")


@get("/custom")
async def get_custom() -> Response[dict]:
    logger.info("get_custom: 201 + X-Request-Id")
    return Response(
        content={"message": "created"},
        status_code=HTTP_201_CREATED,
        headers={"X-Request-Id": "abc-123"},
    )


app = Litestar(route_handlers=[get_json, get_text, get_html, get_redirect, get_custom])
