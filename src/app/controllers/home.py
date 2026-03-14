from litestar import Controller, get
from litestar.response import Template
from dishka.integrations.litestar import FromDishka, inject

from ..services import ProcessManager, LessonScanner


class HomeController(Controller):
    path = "/"

    @get()
    @inject
    async def home(
        self,
        scanner: FromDishka[LessonScanner],
        process_manager: FromDishka[ProcessManager],
    ) -> Template:
        volumes = scanner.scan()
        running_lesson = process_manager.get_running_lesson()
        return Template(
            "home.html",
            context={"volumes": volumes, "running_lesson": running_lesson},
        )
