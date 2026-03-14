from dataclasses import dataclass

from litestar import Litestar, get

from logger_setup import logger


@dataclass
class PlatformInfo:
    platform: str
    framework: str
    description: str


@get("/")
async def about() -> PlatformInfo:
    logger.info("about")
    return PlatformInfo(
        platform="S1T Litestar Workbench",
        framework="Litestar 2.x",
        description="Interactive learning platform for the Litestar framework",
    )


@get("/stack")
async def stack() -> dict:
    logger.info("stack")
    return {
        "backend": "Litestar + Jinja2 + HTMX",
        "di": "Dishka",
        "messaging": "FastStream + RabbitMQ",
        "cache": "Valkey",
        "database": "PostgreSQL + asyncpg",
        "editor": "CodeMirror 6",
    }


@get("/courses")
async def courses() -> dict:
    logger.info("courses")
    return {
        "chapters": [
            {"id": "1_basics", "title": "Basics"},
            {"id": "2_dto", "title": "DTO"},
            {"id": "3_di", "title": "Dependency Injection"},
            {"id": "5_stores", "title": "Stores & Caching"},
        ]
    }


app = Litestar([about, stack, courses])
