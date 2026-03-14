from datetime import datetime

import msgspec


class User(msgspec.Struct):
    username: str
    email: str
    password: str
    id: int | None = None
    role: str = "user"
    created_at: str = ""


_store: dict[int, User] = {}
_counter = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def make_user(username: str, email: str, password: str) -> User:
    uid = next_id()
    user = User(
        username=username,
        email=email,
        password=password,
        id=uid,
        created_at=datetime.now().isoformat(),
    )
    _store[uid] = user
    return user
