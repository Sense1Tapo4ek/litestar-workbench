from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, get
from litestar.exceptions import NotFoundException
from litestar.response import Template

from ..services import LessonScanner, ProcessManager


class VolumeController(Controller):
    path = "/volumes"

    @get("/{volume_id:str}")
    @inject
    async def volume_page(
        self,
        volume_id: str,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
    ) -> Template:
        volumes = scanner.scan()
        volume = next((v for v in volumes if v.id == volume_id), None)
        if volume is None:
            raise NotFoundException(f"Volume '{volume_id}' not found")
        running_lesson = process_manager.get_running_lesson()
        return Template(
            "volume.html",
            context={
                "volume": volume,
                "volumes": volumes,
                "running_lesson": running_lesson,
            },
        )
