from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "My Litestar App"
    debug: bool = False
    max_items: int = Field(default=100, ge=1, le=10000)
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./dev.db"


# Singleton — импортируй из любого места
settings = AppConfig()
