<!-- lang: ru -->
# Redis и StoreRegistry

`RedisStore` — production-замена `MemoryStore`: поддерживает multi-server деплой, персистентность, пространства имён.

## RedisStore

```python
from litestar.stores.redis import RedisStore  # требует: litestar[redis]

# Подключение по URL
store = RedisStore.with_client(url="redis://localhost:6379/0")

# Или с существующим клиентом:
from redis.asyncio import Redis
store = RedisStore(redis=Redis(host="localhost"), namespace="my_app")
```

## ValkeyStore

`ValkeyStore` — API-совместимый аналог RedisStore на базе Valkey (open-source fork Redis):

```python
from litestar.stores.valkey import ValkeyStore  # требует: pip install valkey

store = ValkeyStore.with_client(url="valkey://localhost:6379")
```

## StoreRegistry с пространствами имён

Паттерн для production: один Redis-инстанс, изолированные namespace для каждой фичи:

```python
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry

root_store = RedisStore.with_client(url="redis://localhost")

# Каждый запрос к registry создаёт namespace-изолированный store
stores = StoreRegistry(default_factory=root_store.with_namespace)

app = Litestar(
    stores=stores,
    response_cache_config=ResponseCacheConfig(store="response_cache"),
    middleware=[
        RateLimitConfig(rate_limit=("minute", 100), store="rate_limit").middleware,
        ServerSideSessionConfig(store="sessions").middleware,
    ],
)
```

Ключи `"response_cache"`, `"rate_limit"`, `"sessions"` → разные namespace в Redis.

## Замена MemoryStore на Redis

В этом уроке используется `MemoryStore` для демонстрации. В production просто замените:

```python
# Разработка:
stores = StoreRegistry(default_factory=lambda name: MemoryStore())

# Production (только эта строка меняется):
root = RedisStore.with_client(url=os.environ["REDIS_URL"])
stores = StoreRegistry(default_factory=root.with_namespace)
```

## На что обратить внимание

- `delete_all()` удаляет только ключи текущего namespace, не всего Redis
- `handle_client_shutdown=True` (default) — контейнер закрывает Redis-клиент при shutdown
- `StoreRegistry` — ленивый: store создаётся при первом `app.stores.get(name)`
- `litestar[redis]` включает `redis[asyncio]` как зависимость

<!-- lang: en -->
# Redis and StoreRegistry

`RedisStore` is the production replacement for `MemoryStore`: it supports multi-server deployments, persistence, and namespacing.

## RedisStore

```python
from litestar.stores.redis import RedisStore  # requires: litestar[redis]

# Connect by URL
store = RedisStore.with_client(url="redis://localhost:6379/0")

# Or with an existing client:
from redis.asyncio import Redis
store = RedisStore(redis=Redis(host="localhost"), namespace="my_app")
```

## ValkeyStore

`ValkeyStore` is an API-compatible equivalent of RedisStore based on Valkey (open-source Redis fork):

```python
from litestar.stores.valkey import ValkeyStore  # requires: pip install valkey

store = ValkeyStore.with_client(url="valkey://localhost:6379")
```

## StoreRegistry with namespaces

Production pattern: one Redis instance, isolated namespaces for each feature:

```python
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry

root_store = RedisStore.with_client(url="redis://localhost")

# Each request to the registry creates a namespace-isolated store
stores = StoreRegistry(default_factory=root_store.with_namespace)

app = Litestar(
    stores=stores,
    response_cache_config=ResponseCacheConfig(store="response_cache"),
    middleware=[
        RateLimitConfig(rate_limit=("minute", 100), store="rate_limit").middleware,
        ServerSideSessionConfig(store="sessions").middleware,
    ],
)
```

Keys `"response_cache"`, `"rate_limit"`, `"sessions"` → different namespaces in Redis.

## Replacing MemoryStore with Redis

This lesson uses `MemoryStore` for demonstration purposes. In production, simply replace it:

```python
# Development:
stores = StoreRegistry(default_factory=lambda name: MemoryStore())

# Production (only this line changes):
root = RedisStore.with_client(url=os.environ["REDIS_URL"])
stores = StoreRegistry(default_factory=root.with_namespace)
```

## Things to watch out for

- `delete_all()` deletes only keys in the current namespace, not all of Redis
- `handle_client_shutdown=True` (default) — the container closes the Redis client on shutdown
- `StoreRegistry` is lazy: a store is created on the first `app.stores.get(name)` call
- `litestar[redis]` includes `redis[asyncio]` as a dependency
