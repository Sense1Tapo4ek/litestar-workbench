from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar, get
from litestar.datastructures import State

from logger_setup import logger


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    app.state.visit_count = 0
    app.state.app_name = "S1T Workbench"
    yield


@get("/")
async def index(state: State) -> dict:
    state.visit_count += 1
    logger.info(f"Visit #{state.visit_count}")
    return {
        "app": state.app_name,
        "visits": state.visit_count,
    }


@get("/stats")
async def stats(state: State) -> dict:
    return {
        "total_visits": state.visit_count,
        "app_name": state.app_name,
    }


@get("/reset")
async def reset_counter(state: State) -> dict:
    state.visit_count = 0
    logger.info("Counter reset")
    return {"reset": True, "visits": state.visit_count}


app = Litestar(
    route_handlers=[index, stats, reset_counter],
    lifespan=[lifespan],
)
