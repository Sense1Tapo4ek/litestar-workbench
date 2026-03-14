"""
TestClient — тесты для lesson.py без запуска сервера.

Запусти: python tests.py
"""
from litestar.testing import TestClient

from lesson import app


def test_create_and_get_task():
    with TestClient(app=app) as client:
        # Создаём задачу
        response = client.post("/tasks", json={"title": "Buy milk", "done": False})
        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "Buy milk"
        assert task["done"] is False
        task_id = task["id"]

        # Получаем её по id
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id


def test_list_tasks():
    with TestClient(app=app) as client:
        client.post("/tasks", json={"title": "Task A", "done": False})
        client.post("/tasks", json={"title": "Task B", "done": False})

        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 2


def test_get_nonexistent_task():
    with TestClient(app=app) as client:
        response = client.get("/tasks/99999")
        assert response.status_code == 404


def test_delete_task():
    with TestClient(app=app) as client:
        # Создаём и удаляем
        r = client.post("/tasks", json={"title": "Temp", "done": False})
        task_id = r.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        # Проверяем что удалилась
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 404


if __name__ == "__main__":
    test_create_and_get_task()
    test_list_tasks()
    test_get_nonexistent_task()
    test_delete_task()
    print("All tests passed!")
