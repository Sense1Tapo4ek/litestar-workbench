from typing import Annotated

from litestar import Litestar, Request, get, post
from litestar.params import Parameter
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@get("/info")
async def get_info(request: Request) -> dict:
    logger.info(f"get_info: {request.method} {request.url.path}")
    return {
        "method": request.method,
        "path": request.url.path,
        "client": str(request.client),
        "content_type": request.content_type[0] if request.content_type else None,
    }


@get("/headers-demo")
async def headers_demo(
    user_agent: Annotated[str, Parameter(header="User-Agent")] = "unknown",
    accept: Annotated[str, Parameter(header="Accept")] = "*/*",
    x_request_id: Annotated[str | None, Parameter(header="X-Request-Id")] = None,
) -> dict:
    logger.info(f"headers_demo: ua={user_agent[:30]!r}")
    return {
        "user_agent": user_agent,
        "accept": accept,
        "request_id": x_request_id,
    }


@get("/cookie-demo")
async def cookie_demo(
    theme: Annotated[str, Parameter(cookie="theme")] = "light",
    session_id: Annotated[str | None, Parameter(cookie="session_id")] = None,
) -> dict:
    logger.info(f"cookie_demo: theme={theme} has_session={session_id is not None}")
    return {"theme": theme, "has_session": session_id is not None}


@post("/raw-body", status_code=HTTP_201_CREATED)
async def echo_raw(body: bytes) -> dict:
    logger.info(f"echo_raw: {len(body)}b")
    return {"size": len(body), "preview": body[:50].decode("utf-8", errors="replace")}


app = Litestar(route_handlers=[get_info, headers_demo, cookie_demo, echo_raw])
