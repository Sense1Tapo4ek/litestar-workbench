from dataclasses import dataclass


@dataclass
class Order:
    item: str
    amount: float
    id: int | None = None
    status: str = "pending"


_store: dict[int, Order] = {}
_next_id = 1


def create_order(item: str, amount: float) -> Order:
    global _next_id
    order = Order(id=_next_id, item=item, amount=amount)
    _store[_next_id] = order
    _next_id += 1
    return order


def get_order(order_id: int) -> Order | None:
    return _store.get(order_id)
