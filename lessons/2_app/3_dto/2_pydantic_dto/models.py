from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)
    id: int | None = None
    role: str = "user"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("invalid email format")
        return v.lower()


_store: dict[int, User] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter
