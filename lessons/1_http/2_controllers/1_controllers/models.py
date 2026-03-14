from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    name: str
    price: float
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


_store: dict[int, Item] = {}
_next_id = 1


def create_item(name: str, price: float) -> Item:
    global _next_id
    item = Item(id=_next_id, name=name, price=price)
    _store[_next_id] = item
    _next_id += 1
    return item


def get_item(item_id: int) -> Item | None:
    return _store.get(item_id)


def list_items() -> list[Item]:
    return list(_store.values())


def delete_item(item_id: int) -> bool:
    return _store.pop(item_id, None) is not None
