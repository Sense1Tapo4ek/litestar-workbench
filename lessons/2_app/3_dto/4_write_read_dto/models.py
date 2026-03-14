from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    username: str
    email: str
    password: str
    id: int | None = None
    role: str = "user"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


_store: dict[int, User] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter
