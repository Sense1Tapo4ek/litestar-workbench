from typing import Annotated

from litestar import Litestar, get
from litestar.params import Parameter

from logger_setup import logger


@get("/search")
async def search(
    q: str,
    limit: Annotated[int, Parameter(query="limit", ge=1, le=100)] = 10,
    page: Annotated[int, Parameter(query="page", ge=1)] = 1,
) -> dict:
    logger.info(f"search: q={q!r} limit={limit} page={page}")
    return {
        "query": q,
        "limit": limit,
        "page": page,
        "results": [],
    }


@get("/items/{item_id:int}")
async def get_item(item_id: int) -> dict:
    logger.info(f"get_item: {item_id}")
    return {"id": item_id, "name": f"Item #{item_id}"}


@get("/items/{item_id:int}/reviews")
async def get_reviews(
    item_id: int,
    sort: Annotated[str, Parameter(query="sort")] = "newest",
    verified_only: bool = False,
) -> dict:
    logger.info(f"get_reviews: item={item_id} sort={sort}")
    return {
        "item_id": item_id,
        "sort": sort,
        "verified_only": verified_only,
        "reviews": [],
    }


app = Litestar(route_handlers=[search, get_item, get_reviews])
