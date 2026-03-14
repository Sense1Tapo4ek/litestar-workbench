from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar, get
from litestar.datastructures import State

from logger_setup import logger


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    logger.info("Startup: connecting to DB...")
    app.state.db_connected = True
    app.state.request_count = 0
    logger.info("Startup complete: db_connected=True")
    yield
    logger.info("Shutdown: releasing resources...")
    app.state.db_connected = False
    logger.info("Shutdown complete")


@get("/")
async def index(state: State) -> dict:
    state.request_count += 1
    return {
        "message": "Lifecycle demo",
        "db_connected": state.db_connected,
        "requests_served": state.request_count,
    }


@get("/ready")
async def ready_check(state: State) -> dict:
    return {
        "ready": state.db_connected,
        "requests_so_far": state.request_count,
    }


app = Litestar(
    route_handlers=[index, ready_check],
    lifespan=[lifespan],
)
