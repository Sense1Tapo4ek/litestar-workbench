<!-- lang: ru -->
# AsyncTestClient

`AsyncTestClient` — асинхронная версия TestClient. Используй, когда тесты сами async: нужно `await asyncio.sleep()`, проверять состояние после фоновых задач, или тестировать async контекстные операции.

```python
from litestar.testing import AsyncTestClient
from lesson import app

async def test_submit_job():
    async with AsyncTestClient(app=app) as client:
        response = await client.post("/jobs", json={"task": "process"})
        assert response.status_code == 202

        await asyncio.sleep(0.05)  # ждём обработки

        response = await client.get(f"/jobs/{response.json()['job_id']}")
        assert response.json()["status"] == "done"
```

**Async context manager** — `async with AsyncTestClient(...) as client`.

**Все методы async:** `await client.get()`, `await client.post()`, etc.

**Когда использовать AsyncTestClient вместо TestClient:**
- Тест проверяет поведение после `await asyncio.sleep()`
- Тест использует async fixtures (pytest-asyncio / anyio)
- Тест работает с фоновыми задачами через `asyncio.create_task()`

Смотри `tests.py`. Запусти: `python tests.py`

<!-- lang: en -->
# AsyncTestClient

`AsyncTestClient` is the async version of TestClient. Use it when tests are themselves async: need `await asyncio.sleep()`, check state after background tasks, or test async context operations.

```python
from litestar.testing import AsyncTestClient
from lesson import app

async def test_submit_job():
    async with AsyncTestClient(app=app) as client:
        response = await client.post("/jobs", json={"task": "process"})
        assert response.status_code == 202

        await asyncio.sleep(0.05)  # wait for processing

        response = await client.get(f"/jobs/{response.json()['job_id']}")
        assert response.json()["status"] == "done"
```

**Async context manager** — `async with AsyncTestClient(...) as client`.

**All methods are async:** `await client.get()`, `await client.post()`, etc.

**When to use AsyncTestClient instead of TestClient:**
- Test checks behavior after `await asyncio.sleep()`
- Test uses async fixtures (pytest-asyncio / anyio)
- Test works with background tasks via `asyncio.create_task()`

See `tests.py`. Run: `python tests.py`
