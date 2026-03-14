"""
AsyncTestClient — асинхронные тесты для lesson.py.

Запусти: python tests.py
"""
import asyncio

from litestar.testing import AsyncTestClient

from lesson import app


async def test_submit_and_get_job():
    async with AsyncTestClient(app=app) as client:
        response = await client.post("/jobs", json={"task": "process_data"})
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"
        job_id = data["job_id"]

        # Ждём обработки
        await asyncio.sleep(0.05)

        response = await client.get(f"/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "done"


async def test_list_jobs():
    async with AsyncTestClient(app=app) as client:
        await client.post("/jobs", json={"task": "a"})
        await client.post("/jobs", json={"task": "b"})

        response = await client.get("/jobs")
        assert response.status_code == 200
        assert len(response.json()) >= 2


async def test_get_nonexistent_job():
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/jobs/99999")
        assert response.status_code == 404


if __name__ == "__main__":
    asyncio.run(test_submit_and_get_job())
    asyncio.run(test_list_jobs())
    asyncio.run(test_get_nonexistent_job())
    print("All async tests passed!")
