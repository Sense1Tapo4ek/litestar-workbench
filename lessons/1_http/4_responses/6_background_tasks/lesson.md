<!-- lang: ru -->
# BackgroundTask и BackgroundTasks

`BackgroundTask` позволяет выполнить асинхронную функцию **после** отправки ответа клиенту. Сервер немедленно возвращает ответ (например, 202 Accepted), а фоновая задача запускается уже после.

```python
from litestar.background_tasks import BackgroundTask, BackgroundTasks

return Response(
    content={"status": "queued"},
    background=BackgroundTask(send_email, user_id, "Welcome!"),
)
```

Несколько задач — `BackgroundTasks`:

```python
return Response(
    content={"status": "ok"},
    background=BackgroundTasks(tasks=[
        BackgroundTask(update_stats, endpoint),
        BackgroundTask(write_audit, "create", user_id),
    ]),
)
```

**Когда использовать:**
- Отправка email/SMS после регистрации
- Запись аудит-лога (не блокирует ответ)
- Обновление статистики
- Любые побочные эффекты, не нужные клиенту прямо сейчас

**Ограничения:** BackgroundTask выполняется в той же event loop. Для долгих CPU-bound задач используй Celery/SAQ/ARQ.

<!-- lang: en -->
# BackgroundTask and BackgroundTasks

`BackgroundTask` runs an async function **after** the response is sent to the client. The server returns immediately (e.g., 202 Accepted), and the background task runs afterward.

```python
from litestar.background_tasks import BackgroundTask, BackgroundTasks

return Response(
    content={"status": "queued"},
    background=BackgroundTask(send_email, user_id, "Welcome!"),
)
```

Multiple tasks — use `BackgroundTasks`:

```python
return Response(
    content={"status": "ok"},
    background=BackgroundTasks(tasks=[
        BackgroundTask(update_stats, endpoint),
        BackgroundTask(write_audit, "create", user_id),
    ]),
)
```

**When to use:**
- Send email/SMS after registration
- Write audit logs (doesn't block response)
- Update statistics
- Any side effects the client doesn't need immediately

**Limitations:** BackgroundTask runs in the same event loop. For long CPU-bound work use Celery/SAQ/ARQ.
