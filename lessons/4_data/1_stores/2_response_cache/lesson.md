<!-- lang: ru -->
# Response Cache

Litestar умеет кэшировать HTTP-ответы на уровне роут-хендлера. При повторном запросе хендлер не вызывается — ответ возвращается из кэша.

## Базовое кэширование

```python
from litestar import get
from litestar.config.response_cache import ResponseCacheConfig

@get("/data", cache=5)          # кэш на 5 секунд
async def get_data() -> dict: ...

@get("/static", cache=True)     # кэш на время из ResponseCacheConfig.default_expiration
async def get_static() -> dict: ...
```

- `cache=N` — кэшировать N секунд
- `cache=True` — использовать глобальный `default_expiration` из `ResponseCacheConfig`

## ResponseCacheConfig

```python
from datetime import timedelta
from litestar.config.response_cache import ResponseCacheConfig

app = Litestar(
    route_handlers=[...],
    stores={"response_cache": MemoryStore()},
    response_cache_config=ResponseCacheConfig(
        store="response_cache",        # какой store использовать
        default_expiration=timedelta(minutes=5),
    ),
)
```

## cache_key_builder

По умолчанию ключ кэша = метод + путь + query params. Можно задать свою логику:

```python
from litestar import Request

def key_by_lang(request: Request) -> str:
    return f"greeting:{request.query_params.get('lang', 'en')}"

@get("/greeting", cache=60, cache_key_builder=key_by_lang)
async def greeting(lang: str = "en") -> dict: ...
```

`/greeting?lang=en` и `/greeting?lang=es` — разные ключи → разные записи в кэше.

## Демонстрация кэша

```python
_calls = 0

@get("/compute", cache=5)
async def compute() -> dict:
    global _calls
    _calls += 1
    return {"call_count": _calls}
```

- Запрос 1: `_calls` становится 1, ответ кэшируется
- Запрос 2 (в течение 5с): хендлер НЕ вызывается, `_calls` остаётся 1
- Запрос 3 (после 5с): кэш устарел, хендлер вызывается снова

## На что обратить внимание

- Только GET-ответы с 2xx кэшируются по умолчанию
- Кэш не сбрасывается автоматически — только по истечении TTL
- `cache_key_builder` на хендлере перекрывает глобальный из `ResponseCacheConfig`
- `ResponseCacheConfig(default_expiration=None)` — кэш бессрочно (`cache=True`)

<!-- lang: en -->
# Response Cache

Litestar can cache HTTP responses at the route handler level. On a repeated request the handler is not called — the response is returned from the cache.

## Basic caching

```python
from litestar import get
from litestar.config.response_cache import ResponseCacheConfig

@get("/data", cache=5)          # cache for 5 seconds
async def get_data() -> dict: ...

@get("/static", cache=True)     # cache for the duration set in ResponseCacheConfig.default_expiration
async def get_static() -> dict: ...
```

- `cache=N` — cache for N seconds
- `cache=True` — use the global `default_expiration` from `ResponseCacheConfig`

## ResponseCacheConfig

```python
from datetime import timedelta
from litestar.config.response_cache import ResponseCacheConfig

app = Litestar(
    route_handlers=[...],
    stores={"response_cache": MemoryStore()},
    response_cache_config=ResponseCacheConfig(
        store="response_cache",        # which store to use
        default_expiration=timedelta(minutes=5),
    ),
)
```

## cache_key_builder

By default the cache key = method + path + query params. You can define custom logic:

```python
from litestar import Request

def key_by_lang(request: Request) -> str:
    return f"greeting:{request.query_params.get('lang', 'en')}"

@get("/greeting", cache=60, cache_key_builder=key_by_lang)
async def greeting(lang: str = "en") -> dict: ...
```

`/greeting?lang=en` and `/greeting?lang=es` — different keys → different cache entries.

## Cache demonstration

```python
_calls = 0

@get("/compute", cache=5)
async def compute() -> dict:
    global _calls
    _calls += 1
    return {"call_count": _calls}
```

- Request 1: `_calls` becomes 1, response is cached
- Request 2 (within 5s): handler is NOT called, `_calls` stays at 1
- Request 3 (after 5s): cache expired, handler is called again

## Things to watch out for

- Only GET responses with 2xx status are cached by default
- The cache is not invalidated automatically — only when the TTL expires
- A `cache_key_builder` on a handler overrides the global one from `ResponseCacheConfig`
- `ResponseCacheConfig(default_expiration=None)` — cache indefinitely (`cache=True`)
