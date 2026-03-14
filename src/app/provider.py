from typing import AsyncIterable
from dishka import Provider, Scope, provide

from .services import ScenarioExecutor, ProcessManager, LessonScanner, WorkspaceManager

from .config import LearningConfig


class LearningProvider(Provider):
    """
    DI provider for the Learning context.
    Teaches the container how to create adapters and handle their lifecycle.
    """

    scope = Scope.APP

    @provide
    def get_config(self) -> LearningConfig:
        return LearningConfig()

    @provide
    def get_scanner(self, config: LearningConfig) -> LessonScanner:
        return LessonScanner(
            lessons_dir=config.project_root / config.lessons_dir,
            lesson_port=config.lesson_port,
        )

    @provide
    async def get_process_manager(
        self, config: LearningConfig
    ) -> AsyncIterable[ProcessManager]:
        pm = ProcessManager(config.project_root)
        yield pm
        await pm.stop_all()

    @provide(scope=Scope.APP)
    def get_executor(self, config: LearningConfig) -> ScenarioExecutor:
        return ScenarioExecutor(rabbitmq_url=config.rabbitmq_url)

    @provide
    def get_workspace_manager(self, config: LearningConfig) -> WorkspaceManager:
        return WorkspaceManager(
            workspace_dir=config.project_root / config.workspace_dir,
            lessons_dir=config.project_root / config.lessons_dir,
        )
