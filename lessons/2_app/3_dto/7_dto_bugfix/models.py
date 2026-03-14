from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    name: str
    price: float
    id: int | None = None
    owner_id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


_store: dict[int, Item] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter
