<!-- lang: ru -->
# Rate Limiting

`RateLimitConfig` добавляет middleware ограничения частоты запросов. При превышении лимита возвращается 429 Too Many Requests.

## Базовая настройка

```python
from litestar.middleware.rate_limit import RateLimitConfig

app = Litestar(
    route_handlers=[...],
    middleware=[
        RateLimitConfig(
            rate_limit=("minute", 10),  # 10 запросов в минуту
        ).middleware
    ],
)
```

Единицы времени: `"second"`, `"minute"`, `"hour"`, `"day"`.

## Идентификатор клиента

По умолчанию — IP-адрес клиента. Можно переопределить:

```python
from litestar.connection import ASGIConnection

def get_client_id(connection: ASGIConnection) -> str:
    # По IP
    return connection.client.host if connection.client else "unknown"
    # Или по токену:
    # return connection.headers.get("X-API-Key", connection.client.host)

RateLimitConfig(
    rate_limit=("minute", 100),
    identifier_for_request=get_client_id,
)
```

## Исключения

Глобальные пути и per-route opt:

```python
RateLimitConfig(
    rate_limit=("minute", 10),
    exclude=["/schema", "/health"],     # пути без rate limit
    exclude_opt_key="exclude_from_rl",  # opt-ключ для per-route
)

@get("/public", opt={"exclude_from_rl": True})
async def public() -> dict: ...
```

## Заголовки ответа

```python
RateLimitConfig(
    rate_limit=("minute", 10),
    set_rate_limit_headers=True,  # добавляет RateLimit-* заголовки
)
# Ответ содержит: RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset
```

## На что обратить внимание

- `identifier_for_request` по умолчанию НЕ учитывает `X-Forwarded-For` (безопасность)
- За прокси нужен `ProxyHeadersMiddleware` от uvicorn/hypercorn
- Состояние rate limit хранится в MemoryStore по умолчанию — сбрасывается при перезапуске
- Для multi-server деплоя используйте Redis store: `RateLimitConfig(store="redis_store")`

<!-- lang: en -->
# Rate Limiting

`RateLimitConfig` adds request rate-limiting middleware. When the limit is exceeded, 429 Too Many Requests is returned.

## Basic setup

```python
from litestar.middleware.rate_limit import RateLimitConfig

app = Litestar(
    route_handlers=[...],
    middleware=[
        RateLimitConfig(
            rate_limit=("minute", 10),  # 10 requests per minute
        ).middleware
    ],
)
```

Time units: `"second"`, `"minute"`, `"hour"`, `"day"`.

## Client identifier

The default is the client's IP address. You can override it:

```python
from litestar.connection import ASGIConnection

def get_client_id(connection: ASGIConnection) -> str:
    # By IP
    return connection.client.host if connection.client else "unknown"
    # Or by token:
    # return connection.headers.get("X-API-Key", connection.client.host)

RateLimitConfig(
    rate_limit=("minute", 100),
    identifier_for_request=get_client_id,
)
```

## Exclusions

Global paths and per-route opt:

```python
RateLimitConfig(
    rate_limit=("minute", 10),
    exclude=["/schema", "/health"],     # paths without rate limiting
    exclude_opt_key="exclude_from_rl",  # opt key for per-route exclusion
)

@get("/public", opt={"exclude_from_rl": True})
async def public() -> dict: ...
```

## Response headers

```python
RateLimitConfig(
    rate_limit=("minute", 10),
    set_rate_limit_headers=True,  # adds RateLimit-* headers
)
# Response includes: RateLimit-Limit, RateLimit-Remaining, RateLimit-Reset
```

## Things to watch out for

- `identifier_for_request` does NOT respect `X-Forwarded-For` by default (security)
- Behind a proxy, use `ProxyHeadersMiddleware` from uvicorn/hypercorn
- Rate limit state is stored in MemoryStore by default — resets on restart
- For multi-server deployments, use a Redis store: `RateLimitConfig(store="redis_store")`
