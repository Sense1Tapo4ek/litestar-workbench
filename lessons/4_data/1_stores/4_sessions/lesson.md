<!-- lang: ru -->
# Серверные сессии

`ServerSideSessionConfig` добавляет server-side сессии: данные хранятся на сервере, клиент получает только session ID в cookie.

## Настройка

```python
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.stores.memory import MemoryStore

app = Litestar(
    route_handlers=[...],
    middleware=[ServerSideSessionConfig().middleware],
    stores={"sessions": MemoryStore()},  # store с именем "sessions" (default)
)
```

Данные сессии привязаны к `session_id` в cookie `session` (по умолчанию).

## Работа с сессией в хендлере

```python
from litestar import Request

@get("/me")
async def me(request: Request) -> dict:
    username = request.session.get("username")    # чтение
    return {"username": username}

@post("/login")
async def login(request: Request, ...) -> dict:
    request.session["username"] = "alice"         # запись
    return {"ok": True}

@post("/logout")
async def logout(request: Request) -> dict:
    request.session.clear()                       # очистка
    return {"ok": True}
```

`request.session` — dict-подобный объект. Изменения автоматически сохраняются в store.

## Параметры конфигурации

```python
ServerSideSessionConfig(
    max_age=86400,       # TTL cookie (секунды), default 14 дней
    key="app_session",   # имя cookie, default "session"
    secure=True,         # только HTTPS
    httponly=True,       # нет доступа из JS
    samesite="strict",   # защита от CSRF
    renew_on_access=True, # обновлять TTL при каждом запросе
    store="sessions",    # имя store в registry
)
```

## Server-side vs Cookie-based

| | ServerSide | CookieBacked |
|-|------------|--------------|
| Хранение | Сервер | Клиент (зашифровано) |
| Размер | Без ограничений | Макс ~4KB |
| Безопасность | Высокая | Зависит от шифрования |
| Масштабирование | Нужен общий store | Stateless |

## На что обратить внимание

- Store с именем `"sessions"` должен быть зарегистрирован (иначе auto-MemoryStore)
- `MemoryStore` не переживает перезапуск — используйте FileStore или Redis в prod
- `request.session.clear()` удаляет данные, но cookie остаётся (пустая сессия)

<!-- lang: en -->
# Server-Side Sessions

`ServerSideSessionConfig` adds server-side sessions: data is stored on the server, the client only receives a session ID cookie.

## Setup

```python
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.stores.memory import MemoryStore

app = Litestar(
    route_handlers=[...],
    middleware=[ServerSideSessionConfig().middleware],
    stores={"sessions": MemoryStore()},  # store named "sessions" (default)
)
```

Session data is tied to a `session_id` in the `session` cookie (by default).

## Working with sessions in a handler

```python
from litestar import Request

@get("/me")
async def me(request: Request) -> dict:
    username = request.session.get("username")    # read
    return {"username": username}

@post("/login")
async def login(request: Request, ...) -> dict:
    request.session["username"] = "alice"         # write
    return {"ok": True}

@post("/logout")
async def logout(request: Request) -> dict:
    request.session.clear()                       # clear
    return {"ok": True}
```

`request.session` is a dict-like object. Changes are automatically persisted to the store.

## Configuration parameters

```python
ServerSideSessionConfig(
    max_age=86400,       # cookie TTL (seconds), default 14 days
    key="app_session",   # cookie name, default "session"
    secure=True,         # HTTPS only
    httponly=True,       # no JS access
    samesite="strict",   # CSRF protection
    renew_on_access=True, # renew TTL on every request
    store="sessions",    # store name in registry
)
```

## Server-side vs Cookie-backed

| | ServerSide | CookieBacked |
|-|------------|--------------|
| Storage | Server | Client (encrypted) |
| Size | No limit | Max ~4KB |
| Security | High | Depends on encryption |
| Scaling | Requires shared store | Stateless |

## Things to watch out for

- A store named `"sessions"` must be registered (otherwise auto-MemoryStore)
- `MemoryStore` does not survive restarts — use FileStore or Redis in production
- `request.session.clear()` deletes the data, but the cookie remains (empty session)
