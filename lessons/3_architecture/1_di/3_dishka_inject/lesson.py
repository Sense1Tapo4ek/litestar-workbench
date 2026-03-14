from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, Protocol

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.litestar import (
    FromDishka,
    LitestarProvider,
    inject,
    setup_dishka,
)
from litestar import Litestar, post
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


# --- Domain interfaces (Protocols) ---


class TaskRepository(Protocol):
    async def save_task(self, title: str) -> None: ...


class NotificationService(Protocol):
    async def notify(self, message: str) -> None: ...


class UnitOfWork(Protocol):
    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...


# --- Infrastructure implementations ---


class DbSession:
    async def execute(self, query: str) -> None:
        logger.debug(f"DB execute: {query}")

    async def commit(self) -> None:
        logger.info("DB commit")

    async def rollback(self) -> None:
        logger.warning("DB rollback")

    async def close(self) -> None:
        logger.debug("DB connection closed")


@dataclass
class PostgresTaskRepository:
    session: DbSession

    async def save_task(self, title: str) -> None:
        await self.session.execute(f"INSERT INTO tasks (title) VALUES ('{title}')")


class EmailNotificationService:
    async def notify(self, message: str) -> None:
        if "error" in message.lower():
            raise ValueError(f"Forbidden word in notification: '{message}'")
        logger.info(f"Email sent: {message}")


@dataclass
class DbUnitOfWork:
    session: DbSession

    async def __aenter__(self) -> "DbUnitOfWork":
        logger.debug("UoW: transaction started")
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            logger.warning(f"UoW: caught {exc_type.__name__}, rolling back")
            await self.session.rollback()
        else:
            logger.info("UoW: commit")
            await self.session.commit()


# --- Application service ---


@dataclass
class TaskService:
    repo: TaskRepository
    uow: UnitOfWork
    notifier: NotificationService

    async def create_task(self, title: str) -> dict:
        async with self.uow:
            await self.repo.save_task(title)
            await self.notifier.notify(f"New task: {title}")
        return {"status": "created", "task": title}


# --- DI provider ---


class ApiProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_session(self) -> AsyncGenerator[DbSession, None]:
        logger.debug("DI: opening DB connection")
        session = DbSession()
        yield session
        await session.close()

    repo = provide(PostgresTaskRepository, provides=TaskRepository)
    notifier = provide(EmailNotificationService, provides=NotificationService)
    uow = provide(DbUnitOfWork, provides=UnitOfWork)
    service = provide(TaskService)


# --- Request body + handler ---


@dataclass
class CreateTaskBody:
    title: str


@post("/tasks", status_code=HTTP_201_CREATED)
@inject
async def create_task(data: CreateTaskBody, service: FromDishka[TaskService]) -> dict:
    return await service.create_task(data.title)


container = make_async_container(ApiProvider(), LitestarProvider())
app = Litestar(route_handlers=[create_task])
setup_dishka(container=container, app=app)
