import asyncio

from litestar import Litestar, get, post
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_202_ACCEPTED

from logger_setup import logger

_jobs: dict[int, dict] = {}
_job_counter = 0


@post("/jobs", status_code=HTTP_202_ACCEPTED)
async def submit_job(data: dict[str, str]) -> dict:
    global _job_counter
    _job_counter += 1
    job_id = _job_counter
    _jobs[job_id] = {"id": job_id, "status": "pending", "input": data}
    logger.info(f"submit_job: id={job_id}")
    # Simplified: asyncio.create_task для демонстрации async в тестах
    # В production используй BackgroundTask из litestar.background_tasks
    asyncio.create_task(_process_job(job_id))
    return {"job_id": job_id, "status": "pending"}


async def _process_job(job_id: int) -> None:
    await asyncio.sleep(0.01)
    _jobs[job_id]["status"] = "done"
    logger.info(f"process_job: id={job_id} done")


@get("/jobs/{job_id:int}")
async def get_job(job_id: int) -> dict:
    job = _jobs.get(job_id)
    if job is None:
        raise NotFoundException(f"Job {job_id} not found")
    return job


@get("/jobs")
async def list_jobs() -> list[dict]:
    return list(_jobs.values())


app = Litestar(route_handlers=[submit_job, get_job, list_jobs])
