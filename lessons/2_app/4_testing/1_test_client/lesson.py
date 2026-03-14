from dataclasses import dataclass

from litestar import Litestar, delete, get, post
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from logger_setup import logger


@dataclass
class Task:
    title: str
    done: bool = False
    id: int | None = None


_tasks: dict[int, Task] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter


@post("/tasks", status_code=HTTP_201_CREATED)
async def create_task(data: Task) -> Task:
    task = Task(title=data.title, done=False, id=next_id())
    _tasks[task.id] = task
    logger.info(f"create_task: id={task.id}")
    return task


@get("/tasks/{task_id:int}")
async def get_task(task_id: int) -> Task:
    task = _tasks.get(task_id)
    if task is None:
        raise NotFoundException(f"Task {task_id} not found")
    return task


@get("/tasks")
async def list_tasks() -> list[Task]:
    return list(_tasks.values())


@delete("/tasks/{task_id:int}", status_code=HTTP_204_NO_CONTENT)
async def delete_task(task_id: int) -> None:
    if task_id not in _tasks:
        raise NotFoundException(f"Task {task_id} not found")
    del _tasks[task_id]
    logger.info(f"delete_task: id={task_id}")


app = Litestar(route_handlers=[create_task, get_task, list_tasks, delete_task])
