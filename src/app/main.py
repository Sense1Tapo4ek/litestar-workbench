from pathlib import Path

from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
import uvicorn
from litestar import Litestar
from litestar.static_files import StaticFilesConfig
from litestar.template import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine

from .config import LearningConfig

from .controllers import (
    HomeController,
    LessonController,
    PartialsController,
    ScenarioApiController,
    ServerApiController,
    VolumeController,
    WorkspaceApiController,
)
from .provider import LearningProvider

_APP_DIR = Path(__file__).parent


def create_app() -> Litestar:
    config = LearningConfig()

    app = Litestar(
        route_handlers=[
            HomeController,
            VolumeController,
            LessonController,
            PartialsController,
            ServerApiController,
            ScenarioApiController,
            WorkspaceApiController,
        ],
        template_config=TemplateConfig(
            directory=_APP_DIR.parent / "ui" / "templates",
            engine=JinjaTemplateEngine,
        ),
        static_files_config=[
            StaticFilesConfig(
                directories=[_APP_DIR.parent / "ui" / "static"],
                path="/static",
                name="static",
            )
        ],
        debug=config.debug,
    )

    container = make_async_container(LearningProvider())
    setup_dishka(container, app)

    return app


app = create_app()


def run_cli() -> None:
    config = LearningConfig()
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info",
        app_dir="src",
    )


if __name__ == "__main__":
    run_cli()
