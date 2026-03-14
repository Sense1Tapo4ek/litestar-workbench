from litestar import Litestar, get
from litestar.response import Redirect, Response
from litestar.status_codes import HTTP_201_CREATED
import logger_setup


@get("/json")
async def get_json() -> dict:
    return {"message": "Hello"}


@get("/text")
async def get_text() -> str:
    return "Hello, plain text!"


@get("/redirect")
async def old_endpoint() -> dict:
    return Redirect(path="/json")


@get("/custom", status_code=HTTP_201_CREATED)
async def custom_response() -> dict:
    return Response(content={"created": True}, status_code=200)


app = Litestar(route_handlers=[get_json, get_text, old_endpoint, custom_response])
