from litestar import Litestar, Request, get, post
from litestar.exceptions import (
    HTTPException,
    NotAuthorizedException,
    NotFoundException,
    PermissionDeniedException,
)
from litestar.response import Response
from litestar.status_codes import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
)

from logger_setup import logger

_store: dict[int, dict] = {}
_next_id = 1


@get("/items/{item_id:int}")
async def get_item(item_id: int) -> dict:
    logger.info(f"get_item: {item_id}")
    item = _store.get(item_id)
    if item is None:
        raise NotFoundException(detail=f"Item {item_id} not found")
    return item


@post("/items", status_code=HTTP_201_CREATED)
async def create_item(data: dict) -> dict:
    global _next_id
    if not data.get("name"):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Field 'name' is required",
        )
    for item in _store.values():
        if item["name"] == data["name"]:
            raise HTTPException(
                status_code=HTTP_409_CONFLICT,
                detail=f"Item '{data['name']}' already exists",
            )
    item = {"id": _next_id, **data}
    _store[_next_id] = item
    _next_id += 1
    logger.info(f"create_item: {item['id']} name={item['name']!r}")
    return item


@get("/secret")
async def secret_endpoint() -> dict:
    logger.info("secret_endpoint: raising 401")
    raise NotAuthorizedException(detail="Authentication required")


@get("/admin")
async def admin_endpoint() -> dict:
    logger.info("admin_endpoint: raising 403")
    raise PermissionDeniedException(detail="Admin access only")


@get("/broken")
async def broken_endpoint() -> dict:
    logger.info("broken_endpoint: raising ValueError")
    raise ValueError("Something went wrong internally")


def value_error_handler(request: Request, exc: ValueError) -> Response:
    if isinstance(exc, HTTPException):
        return Response(
            content={"detail": exc.detail},
            status_code=exc.status_code,
        )
    return Response(
        content={"error": str(exc), "type": "ValueError"},
        status_code=HTTP_400_BAD_REQUEST,
    )


def log_exception(exc: Exception, scope: dict) -> None:
    print(f"[after_exception] {type(exc).__name__}: {exc}")


app = Litestar(
    route_handlers=[
        get_item,
        create_item,
        secret_endpoint,
        admin_endpoint,
        broken_endpoint,
    ],
    exception_handlers={ValueError: value_error_handler},
    after_exception=[log_exception],
)
