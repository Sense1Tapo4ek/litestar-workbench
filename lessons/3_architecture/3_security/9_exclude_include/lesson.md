<!-- lang: ru -->
# Исключение эндпоинтов из аутентификации

Два способа сделать эндпоинт публичным при использовании auth backend:

## Метод 1: `exclude` в конфиге auth

```python
jwt_auth = JWTAuth[User](
    ...,
    exclude=["/login", "/public", "/schema"],
)
```

Паттерны URL, которые **никогда** не требуют аутентификации. Подходит для статических открытых маршрутов.

## Метод 2: `exclude_opt_key` + `opt=`

```python
jwt_auth = JWTAuth[User](
    ...,
    exclude_opt_key="exclude_from_auth",
)

@get("/status", opt={"exclude_from_auth": True})
async def status() -> dict: ...
```

Исключает конкретный хендлер через его `opt` метаданные. Удобно когда несколько хендлеров на одном пути требуют разного поведения.

**Правило:** `/schema` (OpenAPI docs) всегда добавляй в `exclude` — иначе Swagger UI не загрузится.

<!-- lang: en -->
# Excluding Endpoints from Authentication

Two ways to make an endpoint public when using an auth backend:

## Method 1: `exclude` in auth config

```python
jwt_auth = JWTAuth[User](
    ...,
    exclude=["/login", "/public", "/schema"],
)
```

URL patterns that **never** require authentication. Good for static public routes.

## Method 2: `exclude_opt_key` + `opt=`

```python
jwt_auth = JWTAuth[User](
    ...,
    exclude_opt_key="exclude_from_auth",
)

@get("/status", opt={"exclude_from_auth": True})
async def status() -> dict: ...
```

Excludes a specific handler via its `opt` metadata. Useful when multiple handlers on the same path need different auth behavior.

**Rule:** Always add `/schema` (OpenAPI docs) to `exclude` — otherwise Swagger UI won't load.
