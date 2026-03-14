from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Product:
    name: str
    price: float
    category: str
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    internal_cost: float = 0.0


_store: dict[int, Product] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter
