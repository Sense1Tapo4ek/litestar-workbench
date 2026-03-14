<!-- lang: ru -->
# TestClient

`TestClient` — синхронный клиент для тестирования Litestar-приложений **без запуска сервера**. Он напрямую вызывает ASGI-приложение.

```python
from litestar.testing import TestClient
from lesson import app

def test_create_task():
    with TestClient(app=app) as client:
        response = client.post("/tasks", json={"title": "Buy milk"})
        assert response.status_code == 201
        assert response.json()["title"] == "Buy milk"
```

**Context manager** (`with TestClient(...) as client`) запускает lifespan приложения (startup/shutdown хуки).

**Методы:** `client.get()`, `client.post()`, `client.put()`, `client.patch()`, `client.delete()` — интерфейс идентичен `httpx`.

**Важно:** `TestClient` синхронный — вызов `client.get("/path")` блокирует выполнение до получения ответа. Это нормально для тестов.

**Изоляция состояния:** `TestClient` не сбрасывает состояние приложения между тестами. Модульные переменные (`_tasks`, `_counter`) сохраняются между вызовами. Для тестовой изоляции используй `pytest` фикстуры или сбрасывай состояние вручную в `setup`/teardown.

Смотри `tests.py` — файл с примерами тестов. Запусти: `python tests.py`

<!-- lang: en -->
# TestClient

`TestClient` is a synchronous client for testing Litestar apps **without running a server**. It calls the ASGI app directly.

```python
from litestar.testing import TestClient
from lesson import app

def test_create_task():
    with TestClient(app=app) as client:
        response = client.post("/tasks", json={"title": "Buy milk"})
        assert response.status_code == 201
        assert response.json()["title"] == "Buy milk"
```

**Context manager** (`with TestClient(...) as client`) runs the app lifespan (startup/shutdown hooks).

**Methods:** `client.get()`, `client.post()`, `client.put()`, `client.patch()`, `client.delete()` — identical interface to `httpx`.

**Important:** `TestClient` is synchronous — `client.get("/path")` blocks until the response is received. This is fine for tests.

**State isolation:** `TestClient` does not reset application state between tests. Module-level variables (`_tasks`, `_counter`) persist across calls. For test isolation use `pytest` fixtures or reset state manually in setup/teardown.

See `tests.py` — file with test examples. Run: `python tests.py`
