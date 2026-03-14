from litestar import Litestar, get
from litestar.connection import ASGIConnection
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.stores.memory import MemoryStore

from logger_setup import logger


def get_client_id(connection: ASGIConnection) -> str:
    return connection.client.host if connection.client else "unknown"


@get("/limited")
async def limited() -> dict:
    logger.info("limited: request accepted")
    return {"status": "ok"}


@get("/unlimited", opt={"exclude_from_rl": True})
async def unlimited() -> dict:
    return {"status": "no rate limit here"}


app = Litestar(
    route_handlers=[limited, unlimited],
    stores={"rate_limit": MemoryStore()},
    middleware=[
        RateLimitConfig(
            rate_limit=("minute", 2),
            identifier_for_request=get_client_id,
            exclude=["/schema"],
            exclude_opt_key="exclude_from_rl",
            store="rate_limit",
        ).middleware
    ],
)
