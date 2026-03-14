<!-- lang: ru -->
# Stores: реализуй кэширование + rate limiting

Задача: добавь два механизма защиты/оптимизации.

## Кэширование ответа

```python
from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.memory import MemoryStore

@get("/report", cache=10)   # кэш на 10 секунд
async def get_report() -> dict: ...

app = Litestar(
    response_cache_config=ResponseCacheConfig(store="response_cache"),
    stores={"response_cache": MemoryStore()},
)
```

Повторные GET /report в течение 10 секунд возвращают кэшированный ответ — `call_count` не растёт.

## Rate Limiting

```python
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.stores.memory import MemoryStore

app = Litestar(
    middleware=[
        RateLimitConfig(
            rate_limit=("minute", 3),
            store="rate_limit",
        ).middleware
    ],
    stores={"rate_limit": MemoryStore()},
)
```

POST /items разрешён не более 3 раз в минуту. После превышения — 429 Too Many Requests.

<!-- lang: en -->
# Stores: Implement Caching + Rate Limiting

Task: add two protection/optimization mechanisms.

## Response Caching

```python
from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.memory import MemoryStore

@get("/report", cache=10)   # cache for 10 seconds
async def get_report() -> dict: ...

app = Litestar(
    response_cache_config=ResponseCacheConfig(store="response_cache"),
    stores={"response_cache": MemoryStore()},
)
```

Repeated GET /report within 10 seconds returns cached response — `call_count` doesn't grow.

## Rate Limiting

```python
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.stores.memory import MemoryStore

app = Litestar(
    middleware=[
        RateLimitConfig(
            rate_limit=("minute", 3),
            store="rate_limit",
        ).middleware
    ],
    stores={"rate_limit": MemoryStore()},
)
```

POST /items allowed max 3 times per minute. Excess requests get 429 Too Many Requests.
