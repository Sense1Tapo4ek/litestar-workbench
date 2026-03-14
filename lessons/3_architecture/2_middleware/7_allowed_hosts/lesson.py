from litestar import Litestar, get
from litestar.config.allowed_hosts import AllowedHostsConfig

from logger_setup import logger


@get("/api/data")
async def get_data() -> dict[str, str]:
    logger.info("get_data: request accepted")
    return {"data": "secret", "status": "ok"}


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "alive"}


app = Litestar(
    route_handlers=[get_data, health],
    allowed_hosts=AllowedHostsConfig(
        allowed_hosts=["localhost", "127.0.0.1", "testserver"],
        www_redirect=False,
    ),
)
