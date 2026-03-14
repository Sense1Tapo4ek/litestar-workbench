from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InfraConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="S1T_")

    valkey_url: str = "valkey://localhost:6379"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/learn_litestar",
        validation_alias=AliasChoices("DATABASE_URL", "S1T_DATABASE_URL"),
    )


infra = InfraConfig()
