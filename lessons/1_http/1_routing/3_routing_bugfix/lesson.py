from litestar import Litestar, get
from litestar.status_codes import HTTP_201_CREATED


@get("/orders")
async def list_orders() -> list[dict]:
    return [{"id": 1, "status": "pending"}]


@get("/orders", status_code=HTTP_201_CREATED)
async def create_order(data: dict) -> dict:
    return {"id": 2, "status": "created", **data}


@get("/products/{product_id:int}")
async def get_product(product_id: str) -> dict:
    return {"id": product_id, "name": "Widget"}


@get("/health")
async def health() -> dict:
    return {"status": "ok"}


app = Litestar(route_handlers=[list_orders, create_order, health])
