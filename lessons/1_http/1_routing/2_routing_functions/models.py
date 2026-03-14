from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Item:
    name: str
    price: float
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# In-memory store for this lesson
_store: dict[int, Item] = {}
_counter = 0


def create_item(name: str, price: float) -> Item:
    global _counter
    _counter += 1
    item = Item(id=_counter, name=name, price=price)
    _store[_counter] = item
    return item


def get_item(item_id: int) -> Item | None:
    return _store.get(item_id)


def list_items() -> list[Item]:
    return list(_store.values())


def update_item(item_id: int, **fields) -> Item | None:
    item = _store.get(item_id)
    if item is None:
        return None
    for k, v in fields.items():
        setattr(item, k, v)
    return item


def delete_item(item_id: int) -> bool:
    return _store.pop(item_id, None) is not None
