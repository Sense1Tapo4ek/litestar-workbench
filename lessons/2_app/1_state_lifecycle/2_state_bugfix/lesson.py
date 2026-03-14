from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar, get
from litestar.datastructures import ImmutableState, State
import logger_setup


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncGenerator[None, None]:
    app.state.visits = 0
    app.state.app_name = "Demo"
    yield


@get("/")
async def index(state: State) -> dict:
    state.visit_count += 1
    return {"app": state.app_name, "visits": state.visit_count}


@get("/stats")
async def get_stats(state: State) -> dict:
    state.visit_count += 1
    return {"total": state.visit_count, "app": state.app_name}


app = Litestar(
    route_handlers=[index, get_stats],
    lifespan=[lifespan],
    state=ImmutableState({"db_url": "sqlite:///app.db"}),
)
