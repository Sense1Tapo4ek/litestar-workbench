from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, get
from litestar.exceptions import NotFoundException
from litestar.response import Template

from ..models import LessonMode, ServerStatus

from ..services import (
    LessonScanner,
    ProcessManager,
    WorkspaceManager,
)


class LessonController(Controller):
    path = "/lessons"

    @get("/{volume_id:str}/{chapter_id:str}/{lesson_id:str}")
    @inject
    async def lesson_page(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
        workspace_manager: FromDishka[WorkspaceManager],
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

        all_lessons = [
            (v, c, l) for v in volumes for c in v.chapters for l in c.lessons
        ]
        idx = next(
            (
                i
                for i, (v, c, l) in enumerate(all_lessons)
                if v.id == volume_id and c.id == chapter_id and l.id == lesson_id
            ),
            None,
        )
        prev_lesson = all_lessons[idx - 1] if idx and idx > 0 else None
        next_lesson = (
            all_lessons[idx + 1]
            if idx is not None and idx + 1 < len(all_lessons)
            else None
        )

        theory_html = scanner.get_theory_html(volume_id, chapter_id, lesson_id, lang="ru")
        theory_html_en = scanner.get_theory_html(volume_id, chapter_id, lesson_id, lang="en")
        lesson_files = scanner.get_lesson_files(volume_id, chapter_id, lesson_id)
        scenario = (
            scanner.get_scenario(volume_id, chapter_id, lesson_id)
            if lesson.has_scenario
            else None
        )
        server_status = process_manager.get_status(volume_id, chapter_id, lesson_id)
        conflict_with = None
        if server_status == ServerStatus.STOPPED:
            running = process_manager.get_running_lesson()
            if running and running != (volume_id, chapter_id, lesson_id):
                server_status = ServerStatus.CONFLICT
                conflict_with = running

        active_dir = workspace_manager.get_active_dir(volume_id, chapter_id, lesson_id)
        raw_files = scanner.get_lesson_files_raw(
            volume_id, chapter_id, lesson_id, source_dir=active_dir
        )
        has_modifications = workspace_manager.has_modifications(
            volume_id, chapter_id, lesson_id
        )
        file_modified_map = {}
        for fname in raw_files:
            file_modified_map[fname] = workspace_manager.is_file_modified(
                volume_id, chapter_id, lesson_id, fname
            )

        return Template(
            "lesson.html",
            context={
                "volume": volume,
                "chapter": chapter,
                "lesson": lesson,
                "volume_id": volume_id,
                "chapter_id": chapter_id,
                "lesson_id": lesson_id,
                "volumes": volumes,
                "prev_lesson": prev_lesson,
                "next_lesson": next_lesson,
                "theory_html": theory_html,
                "theory_html_en": theory_html_en,
                "lesson_files": lesson_files,
                "active_file": lesson_files[0].filename if lesson_files else None,
                "scenario": scenario,
                "server_status": server_status,
                "conflict_with": conflict_with,
                "ServerStatus": ServerStatus,
                "LessonMode": LessonMode,
                "raw_files": raw_files,
                "has_modifications": has_modifications,
                "file_modified_map": file_modified_map,
            },
        )


class PartialsController(Controller):
    path = "/partials"

    @get("/chapter/{volume_id:str}/{chapter_id:str}")
    @inject
    async def chapter_lessons(
        self,
        volume_id: str,
        chapter_id: str,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
    ) -> Template:
        volumes = scanner.scan()
        volume = next((v for v in volumes if v.id == volume_id), None)
        if volume is None:
            raise NotFoundException(f"Volume '{volume_id}' not found")
        chapter = next((c for c in volume.chapters if c.id == chapter_id), None)
        if chapter is None:
            raise NotFoundException(f"Chapter '{chapter_id}' not found")
        running_lesson = process_manager.get_running_lesson()
        return Template(
            "partials/lesson_list.html",
            context={"chapter": chapter, "running_lesson": running_lesson},
        )

    @get("/code/{volume_id:str}/{chapter_id:str}/{lesson_id:str}/{filename:str}")
    @inject
    async def code_tab(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        filename: str,
        scanner: FromDishka[LessonScanner],
    ) -> Template:
        files = scanner.get_lesson_files(volume_id, chapter_id, lesson_id)
        f = next((f for f in files if f.filename == filename), None)
        if f is None:
            raise NotFoundException(f"File '{filename}' not found")
        return Template(
            "partials/code_tab.html",
            context={
                "file": f,
                "volume_id": volume_id,
                "chapter_id": chapter_id,
                "lesson_id": lesson_id,
                "all_files": files,
                "active_file": filename,
            },
        )
