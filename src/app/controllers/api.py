from dataclasses import dataclass

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, get, post
from litestar.exceptions import NotFoundException
from litestar.response import ServerSentEvent, Template

from ..models import ServerStatus

from ..services import (
    LessonScanner,
    ProcessManager,
    ScenarioExecutor,
    WorkspaceManager,
    stream_log_events,
)


class ServerApiController(Controller):
    path = "/api/server"

    @post("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/start")
    @inject
    async def start_server(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
        workspace_manager: FromDishka[WorkspaceManager],
        executor: FromDishka[ScenarioExecutor],
    ) -> Template:
        volumes = scanner.scan()
        volume = next((v for v in volumes if v.id == volume_id), None)
        if volume is None:
            raise NotFoundException(f"Volume '{volume_id}' not found")
        chapter = next((c for c in volume.chapters if c.id == chapter_id), None)
        if chapter is None:
            raise NotFoundException(f"Chapter '{chapter_id}' not found")
        lesson = next((l for l in chapter.lessons if l.id == lesson_id), None)
        if lesson is None:
            raise NotFoundException(f"Lesson '{lesson_id}' not found")

        executor.reset_context()
        cwd = workspace_manager.get_active_dir(volume_id, chapter_id, lesson_id)
        status = await process_manager.start(
            volume_id, chapter_id, lesson_id, lesson.port, cwd=cwd
        )
        conflict_with = (
            process_manager.get_running_lesson()
            if status == ServerStatus.CONFLICT
            else None
        )
        return Template(
            "partials/server_controls.html",
            context={
                "volume_id": volume_id,
                "chapter_id": chapter_id,
                "lesson_id": lesson_id,
                "lesson": lesson,
                "server_status": status,
                "ServerStatus": ServerStatus,
                "conflict_with": conflict_with,
            },
        )

    @post("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/stop")
    @inject
    async def stop_server(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
    ) -> Template:
        volumes = scanner.scan()
        volume = next((v for v in volumes if v.id == volume_id), None)
        chapter = next((c for c in volume.chapters if c.id == chapter_id), None) if volume else None
        lesson = (
            next((l for l in chapter.lessons if l.id == lesson_id), None)
            if chapter
            else None
        )

        await process_manager.stop(volume_id, chapter_id, lesson_id)
        return Template(
            "partials/server_controls.html",
            context={
                "volume_id": volume_id,
                "chapter_id": chapter_id,
                "lesson_id": lesson_id,
                "lesson": lesson,
                "server_status": ServerStatus.STOPPED,
                "ServerStatus": ServerStatus,
            },
        )

    @get("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/logs")
    @inject
    async def logs_stream(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        process_manager: FromDishka[ProcessManager],
    ) -> ServerSentEvent:
        async def event_generator():
            async for html in stream_log_events(
                process_manager, volume_id, chapter_id, lesson_id
            ):
                yield {"data": html, "event": "log"}

        return ServerSentEvent(event_generator())


class ScenarioApiController(Controller):
    path = "/api/scenario"

    @post("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/{step_id:int}/execute")
    @inject
    async def execute_step(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        step_id: int,
        scanner: FromDishka[LessonScanner],
        executor: FromDishka[ScenarioExecutor],
    ) -> Template:
        scenario = scanner.get_scenario(volume_id, chapter_id, lesson_id)
        if scenario is None or step_id >= len(scenario.steps):
            raise NotFoundException("Step not found")

        step = scenario.steps[step_id]
        volumes = scanner.scan()
        volume = next((v for v in volumes if v.id == volume_id), None)
        chapter = next((c for c in volume.chapters if c.id == chapter_id), None) if volume else None
        lesson = (
            next((l for l in chapter.lessons if l.id == lesson_id), None)
            if chapter
            else None
        )
        port = lesson.port if lesson else 8100

        result = await executor.execute_step(step, port)
        return Template(
            "partials/step_result.html",
            context={"result": result, "step": step},
        )


@dataclass
class SaveFileBody:
    filename: str
    content: str


class WorkspaceApiController(Controller):
    path = "/api/workspace"

    @post("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/save")
    @inject
    async def save_file(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        data: SaveFileBody,
        workspace_manager: FromDishka[WorkspaceManager],
    ) -> dict[str, str]:
        workspace_manager.save_file(
            volume_id, chapter_id, lesson_id, data.filename, data.content
        )
        modified = workspace_manager.is_file_modified(
            volume_id, chapter_id, lesson_id, data.filename
        )
        return {"status": "saved", "modified": str(modified).lower()}

    @post("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/reset")
    @inject
    async def reset_workspace(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        workspace_manager: FromDishka[WorkspaceManager],
        scanner: FromDishka[LessonScanner],
    ) -> dict[str, dict[str, str]]:
        workspace_manager.reset_workspace(volume_id, chapter_id, lesson_id)
        files = scanner.get_lesson_files_raw(volume_id, chapter_id, lesson_id)
        return {"files": files}

    @get("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/files")
    @inject
    async def get_files(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        workspace_manager: FromDishka[WorkspaceManager],
        scanner: FromDishka[LessonScanner],
    ) -> dict:
        active_dir = workspace_manager.get_active_dir(volume_id, chapter_id, lesson_id)
        files = scanner.get_lesson_files_raw(
            volume_id, chapter_id, lesson_id, source_dir=active_dir
        )
        result = []
        for name, content in files.items():
            modified = workspace_manager.is_file_modified(
                volume_id, chapter_id, lesson_id, name
            )
            result.append({"name": name, "content": content, "modified": modified})
        return {"files": result}
