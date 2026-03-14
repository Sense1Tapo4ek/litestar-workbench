import asyncio

from litestar import Litestar, get, post
from litestar.background_tasks import BackgroundTask, BackgroundTasks
from litestar.response import Response
from litestar.status_codes import HTTP_202_ACCEPTED

from logger_setup import logger

_audit_log: list[str] = []


async def send_notification(user_id: int, message: str) -> None:
    await asyncio.sleep(0.01)
    entry = f"notify: user={user_id} msg={message}"
    _audit_log.append(entry)
    logger.info(entry)


async def update_stats(endpoint: str) -> None:
    await asyncio.sleep(0.005)
    entry = f"stats: endpoint={endpoint}"
    _audit_log.append(entry)
    logger.info(entry)


async def write_audit(action: str, user_id: int) -> None:
    await asyncio.sleep(0.005)
    entry = f"audit: action={action} user={user_id}"
    _audit_log.append(entry)
    logger.info(entry)


@post("/notify/{user_id:int}", status_code=HTTP_202_ACCEPTED)
async def notify_user(user_id: int) -> Response[dict]:
    logger.info(f"notify_user: scheduling bg task for user={user_id}")
    return Response(
        content={"status": "queued", "user_id": user_id},
        background=BackgroundTask(send_notification, user_id, "Welcome!"),
    )


@post("/process/{user_id:int}", status_code=HTTP_202_ACCEPTED)
async def process_user(user_id: int) -> Response[dict]:
    logger.info(f"process_user: scheduling multiple bg tasks for user={user_id}")
    return Response(
        content={"status": "processing", "user_id": user_id},
        background=BackgroundTasks(
            tasks=[
                BackgroundTask(update_stats, "/process"),
                BackgroundTask(write_audit, "process", user_id),
            ]
        ),
    )


@get("/audit-log")
async def get_audit_log() -> dict:
    return {"entries": list(_audit_log), "count": len(_audit_log)}


app = Litestar(route_handlers=[notify_user, process_user, get_audit_log])
