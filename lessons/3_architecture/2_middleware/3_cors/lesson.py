from litestar import Litestar, get, post
from litestar.config.cors import CORSConfig

from logger_setup import logger


@get("/api/public")
async def public_data() -> dict[str, str]:
    logger.info("public_data: request received")
    return {"data": "public info", "source": "s1t-api"}


@get("/api/private")
async def private_data() -> dict[str, str]:
    logger.info("private_data: request received")
    return {"data": "private info", "secret": "42"}


@post("/api/items")
async def create_item(data: dict[str, str]) -> dict[str, str]:
    logger.info(f"create_item: {data}")
    return {"id": "1", **data}


cors_config = CORSConfig(
    allow_origins=["https://frontend.example.com", "http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Custom-Header"],
    allow_credentials=True,
    expose_headers=["X-Total-Count"],
    max_age=600,
)

app = Litestar(
    route_handlers=[public_data, private_data, create_item],
    cors_config=cors_config,
)
