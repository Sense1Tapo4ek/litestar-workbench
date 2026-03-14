from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class LearningConfig(BaseSettings):
    """
    Configuration for the Learning context.
    """

    model_config = SettingsConfigDict(
        env_prefix="S1T_", env_file=".env", extra="ignore"
    )

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    lessons_dir: Path = Path("lessons")
    project_root: Path = Path(".")
    lesson_port: int = 8200
    workspace_dir: Path = Path(".workspaces")

    valkey_url: str = "valkey://localhost:6379"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
