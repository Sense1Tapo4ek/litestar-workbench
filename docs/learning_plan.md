# Litestar Learning Platform — Plan v5

> **Version:** 5.0 | **Date:** 2026-03-11
> **Hierarchy:** Volume > Chapter > Lesson
> **Total:** 7 volumes, 24 chapters, 117 lessons (61 done, 56 new)

---

## Summary

| Том | Название | Глав | Уроков | Done | New | Приоритет |
|-----|----------|------|--------|------|-----|-----------|
| 0 | Платформа | 1 | 7 | 7 | 0 | — |
| 1 | Основы HTTP | 4 | 19 | 18 | 1 | Phase 1 |
| 2 | Приложение Litestar | 5 | 17 | 11 | 6 | Phase 1 |
| 3 | Архитектура | 3 | 22 | 20 | 2 | Phase 1 |
| 4 | Данные & Хранение | 2 | 13 | 5 | 8 | Phase 1-2 |
| 5 | Frontend & Realtime | 3 | 15 | 0 | 15 | Phase 3 |
| 6 | Интеграции & Production | 5 | 24 | 0 | 24 | Phase 4 |
| **Total** | | **24** | **117** | **61** | **56** | |

**Изменения v4 → v5:**
- Phase 0 (Restructure) — DONE, убран из roadmap
- Перенос `BackgroundTask` из 6.1 в 1.4 (потребность возникает рано)
- Перенос `TestClient` + `AsyncTestClient` из 6.3 в новую Главу 2.4
- Новая Глава 2.5 — Configuration (pydantic-settings)
- Добавлен `7_alembic_setup` в 4.2 SQLAlchemy
- Добавлен `6_ws_auth` в 5.2 WebSockets
- Глава 6.1 переименована: Events (без BackgroundTasks)
- Глава 6.3 сокращена: 2 урока (advanced testing only)

---

## Dependency Graph

```
Том 0 (Платформа)
  │
  v
Том 1 (Основы HTTP) ──────────────────────────────────────┐
  │                                                        │
  v                                                        v
Том 2 (Приложение) ──> Том 3 (Архитектура)          Том 5 (Frontend & Realtime)
                         │                                 │
                         v                                 │
                       Том 4 (Данные & Хранение)           │
                         │                                 │
                         v                                 v
                       Том 6 (Интеграции & Production) <───┘
```

Правила:
- Том N может зависеть от томов 0..N-1, но **не наоборот**
- Том 5 зависит только от Тома 1 (routing, responses) — не от Тома 3
- Том 6 зависит от всех предыдущих томов

---

## Директории (целевая структура)

```
lessons/
├── 0_platform/
│   ├── volume.yaml
│   └── 0_guide/
│       ├── chapter.yaml
│       ├── 1_welcome/
│       │   ├── lesson.yaml
│       │   ├── lesson.py
│       │   ├── lesson.md
│       │   └── scenario.yaml
│       └── .../
├── 1_http/
│   ├── volume.yaml
│   ├── 1_routing/
│   ├── 2_controllers/
│   ├── 3_request/
│   └── 4_responses/
├── 2_app/
│   ├── volume.yaml
│   ├── 1_state_lifecycle/
│   ├── 2_openapi_cli/
│   ├── 3_dto/
│   ├── 4_testing/          # NEW (перенесено из 6.3)
│   └── 5_config/           # NEW (pydantic-settings)
├── 3_architecture/
│   ├── volume.yaml
│   ├── 1_di/
│   ├── 2_middleware/
│   └── 3_security/
├── 4_data/
│   ├── volume.yaml
│   ├── 1_stores/
│   └── 2_sqlalchemy/
├── 5_frontend/
│   ├── volume.yaml
│   ├── 1_templates/
│   ├── 2_websockets/
│   └── 3_htmx/
└── 6_production/
    ├── volume.yaml
    ├── 1_events/
    ├── 2_faststream/
    ├── 3_testing_advanced/  # Только dependency override + мокинг
    ├── 4_observability/
    └── 5_advanced/
```

---

## Том 0 — Платформа

> Онбординг: как работать с S1T Litestar Workbench.

### Глава 0.1 — Знакомство с платформой (7 уроков) — DONE

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_welcome` | Welcome | tutorial | DONE |
| 2 | `2_about` | О платформе и курсе | tutorial | DONE |
| 3 | `3_http` | HTTP: Заголовки и Куки | tutorial | DONE |
| 4 | `4_ws` | WebSockets | tutorial | DONE |
| 5 | `5_infra` | Внешние сервисы | tutorial | DONE |
| 6 | `6_challenge` | Challenge Example | challenge | DONE |
| 7 | `7_bugfix` | Bugfix Example | bugfix | DONE |

**Docs:** N/A (platform-specific)

---

## Том 1 — Основы HTTP

> Фундамент: маршруты, хендлеры, входящие данные, ответы, ошибки.
> **Зависимости:** Том 0

### Глава 1.1 — Routing (5 уроков) — DONE

Минимальное приложение, HTTP-методы, path params, расширенный роутинг.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_hello_world` | Hello World | tutorial | DONE |
| 2 | `2_routing_functions` | Функциональные хендлеры | tutorial | DONE |
| 3 | `3_routing_bugfix` | Routing: найди ошибки | bugfix | DONE |
| 4 | `4_routing_advanced` | Расширенный роутинг | tutorial | DONE |
| 5 | `5_routing_challenge` | Routing: реализуй хендлеры | challenge | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/routing/

**Ключевые концепции:**
- `@get/@post/@put/@patch/@delete`, `@route()` multi-method
- Path params (int/str/float/uuid/date/path), список путей
- `opt` metadata, `name=`, `route_reverse()`, `sync_to_thread`

---

### Глава 1.2 — Controllers & Routers (3 урока) — DONE

Организация хендлеров в классы и вложенные группы.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_controllers` | Controller | tutorial | DONE |
| 2 | `2_controllers_bugfix` | Controller: найди ошибки | bugfix | DONE |
| 3 | `3_routers` | Router | tutorial | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/routing/handlers/ , https://docs.litestar.dev/latest/usage/routing/routers/

**Ключевые концепции:**
- `Controller`, `path`, class-level `tags`/`guards`/`dependencies`
- `Router`, вложенность, guard/dependency inheritance

---

### Глава 1.3 — Request Data (5 уроков) — DONE

Получение данных из запроса: query, body, формы, файлы, объект Request.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_query_params` | Query параметры | tutorial | DONE |
| 2 | `2_query_challenge` | Query: реализуй поиск | challenge | DONE |
| 3 | `3_request_body` | Тело запроса | tutorial | DONE |
| 4 | `4_body_challenge` | Body: реализуй API | challenge | DONE |
| 5 | `5_request_special` | Объект Request и специальные параметры | tutorial | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/request-data/

**Ключевые концепции:**
- Query params: обязательные vs optional, `Parameter`, `Annotated`, validators
- Body: `data: Model`, `Body(media_type=...)`, `UploadFile`, `request_max_body_size`
- `Request` injection, raw body, headers/cookies via `Parameter`

---

### Глава 1.4 — Responses & Errors (6 уроков) — 5 DONE + 1 NEW

Типы ответов, потоки, файлы, SSE, фоновые задачи, обработка ошибок.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_responses_basic` | Типы ответов | tutorial | DONE |
| 2 | `2_responses_bugfix` | Responses: найди ошибки | bugfix | DONE |
| 3 | `3_responses_advanced` | Расширенные ответы | tutorial | DONE |
| 4 | `4_error_handling` | Обработка ошибок | tutorial | DONE |
| 5 | `5_error_handling_challenge` | Error handling: реализуй обработчики | challenge | DONE |
| 6 | `6_background_tasks` | BackgroundTask и BackgroundTasks | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/responses/ , https://docs.litestar.dev/latest/usage/exceptions/

**Ключевые концепции:**
- JSON, `MediaType.TEXT/HTML`, `Redirect`, `Response[T]`, `CacheControlHeader`, `ETag`
- `Stream`, `File`, `BackgroundTask`, `ServerSentEvent`, MessagePack
- `HTTPException` hierarchy, `exception_handlers`, `ValidationException.extra`
- Layered handlers (ASGI 404/405 — только app-уровень), `after_exception`
- `BackgroundTask(fn, *args)`, `BackgroundTasks([...])` — выполняются после отправки ответа

**Почему BackgroundTasks здесь, а не в Томе 6:**
`BackgroundTask` привязан к `Response` — это часть response pipeline. Потребность "ответить 200 OK и отправить email" возникает рано. Паттерн `Response(..., background=BackgroundTask(...))` логически продолжает тему ответов.

---

## Том 2 — Приложение Litestar

> Жизненный цикл приложения, слоёная архитектура, инструменты разработчика, DTO, тестирование, конфигурация.
> **Зависимости:** Том 1

### Глава 2.1 — State & Lifecycle (4 урока) — DONE

Состояние приложения, хуки жизненного цикла, слоёная архитектура.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_state` | State | tutorial | DONE |
| 2 | `2_state_bugfix` | State: найди ошибки | bugfix | DONE |
| 3 | `3_lifecycle` | Хуки жизненного цикла | tutorial | DONE |
| 4 | `4_layered_arch` | Слоёная архитектура | tutorial | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/the-litestar-app/

**Ключевые концепции:**
- `State`, `ImmutableState`, `initial_state=`, per-request state
- `lifespan` context manager, `before_request`, `after_request`, `after_response`
- Наследование App -> Router -> Controller -> Handler: guards accumulate, dependencies override, response_headers merge

---

### Глава 2.2 — OpenAPI & CLI (2 урока) — DONE

Инструменты разработчика: автогенерация документации и CLI.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_openapi` | OpenAPI | tutorial | DONE |
| 2 | `2_cli` | Litestar CLI | tutorial | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/openapi/ , https://docs.litestar.dev/latest/usage/cli/

**Ключевые концепции:**
- `OpenAPIConfig`, UI plugins (Swagger/ReDoc/Elements/RapiDoc)
- `tags`, `include_in_schema=False`, `summary`/`description`
- `litestar run/routes/schema`, `--reload/--port`, `LITESTAR_APP`

---

### Глава 2.3 — DTO (7 уроков) — 5 DONE + 2 NEW

Data Transfer Objects: фильтрация, сериализация, разделение read/write, partial update.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_dataclass_dto` | DataclassDTO | tutorial | DONE |
| 2 | `2_pydantic_dto` | PydanticDTO | tutorial | DONE |
| 3 | `3_msgspec_dto` | MsgspecDTO | tutorial | DONE |
| 4 | `4_write_read_dto` | Write/Read DTO | tutorial | DONE |
| 5 | `5_dto_data` | DTOData и PATCH | tutorial | DONE |
| 6 | `6_dto_challenge` | DTO: реализуй CRUD с разделением write/read | challenge | **NEW** |
| 7 | `7_dto_bugfix` | DTO: найди ошибки | bugfix | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/dto/

**Ключевые концепции:**
- `DTOConfig`: exclude, rename_fields, rename_strategy, partial
- `data.create_instance(**extra)` (POST), `data.update_instance(obj)` (PATCH)
- Разделение `dto=` / `return_dto=` для write/read схем

---

### Глава 2.4 — Testing Basics (2 урока) — NEW

Базовое тестирование: TestClient для маршрутов и DTO.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_test_client` | TestClient: синхронное тестирование | tutorial | **NEW** |
| 2 | `2_async_test_client` | AsyncTestClient: асинхронное тестирование | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/testing/

**Ключевые концепции:**
- `TestClient(app)`, `client.get()`, `client.post()`, assertions
- `AsyncTestClient(app)`, async test patterns
- Тестирование маршрутов, DTO, error handlers

**Почему тестирование здесь, а не в Томе 6:**
Студент должен уметь тестировать свои маршруты и DTO сразу после их изучения. Откладывать TestClient до Phase 4 — стратегическая ошибка. Продвинутые темы (dependency override, мокинг брокеров) остаются в 6.3.

---

### Глава 2.5 — Configuration (1 урок) — NEW

Управление конфигурацией приложения через pydantic-settings.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_pydantic_settings` | Конфигурация: pydantic-settings и .env | tutorial | **NEW** |

**Docs:** https://docs.pydantic.dev/latest/concepts/pydantic_settings/

**Ключевые концепции:**
- `BaseSettings`, `env_prefix`, `.env` файлы, `model_config`
- Разделение dev/prod конфигурации
- Секреты: DATABASE_URL, JWT_SECRET, API keys — не хардкодить

**Почему отдельная глава:**
Конфигурация — интеграционная тема: `.env`, pydantic-settings, переменные окружения. Не привязана к State/Lifecycle, используется повсеместно начиная с Тома 3 (DI, security) и далее.

---

## Том 3 — Архитектура

> Dependency Injection, middleware pipeline, безопасность и аутентификация.
> **Зависимости:** Том 2

### Глава 3.1 — Dependency Injection (6 уроков) — DONE

Встроенный DI Litestar + Dishka: провайдеры, скоупы, тестирование.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_builtin_di` | Встроенный DI | tutorial | DONE |
| 2 | `2_dishka_basics` | Dishka: основы и инъекция | tutorial | DONE |
| 3 | `3_dishka_inject` | Dishka: скоупы и UoW | tutorial | DONE |
| 4 | `4_dishka_providers` | Dishka: провайдеры | tutorial | DONE |
| 5 | `5_dishka_testing` | Dishka: тестирование | tutorial | DONE |
| 6 | `6_dishka_scopes` | Dishka: SESSION scope | tutorial | DONE |

**Docs:** https://docs.litestar.dev/latest/usage/dependency-injection/ , https://dishka.readthedocs.io/

**Ключевые концепции:**
- `Provide`, `Dependency(skip_validation, default)`, generator deps, dependency chains
- `Provider`, `Scope.APP/REQUEST/SESSION`, `@provide`, `make_async_container`
- `@inject`, `FromDishka[T]`, `setup_dishka`, override providers

---

### Глава 3.2 — Middleware (7 уроков) — 6 DONE + 1 NEW

ASGI middleware pipeline: порядок выполнения, встроенные middleware, кастомные.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_middleware_intro` | Введение в Middleware | tutorial | DONE |
| 2 | `2_custom_middleware` | Кастомный Middleware | tutorial | DONE |
| 3 | `3_cors` | CORS | tutorial | DONE |
| 4 | `4_csrf` | CSRF-защита | tutorial | DONE |
| 5 | `5_compression` | Сжатие ответов | tutorial | DONE |
| 6 | `6_middleware_bugfix` | Middleware: найди ошибки | bugfix | DONE |
| 7 | `7_allowed_hosts` | AllowedHostsMiddleware | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/middleware/

**Ключевые концепции:**
- MiddlewareProtocol, onion model, порядок вызова
- CORSConfig, CSRFConfig, CompressionConfig, AllowedHostsConfig
- Pure ASGI middleware: scope/receive/send

---

### Глава 3.3 — Security & Auth (9 уроков) — 8 DONE + 1 NEW

Guards (access control) + Security Backends (SessionAuth, JWT, OAuth2).

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_guards_intro` | Введение в Guards | tutorial | DONE |
| 2 | `2_guards_layered` | Guards: накопление по слоям | tutorial | DONE |
| 3 | `3_guards_auth` | Аутентификация через Middleware | tutorial | DONE |
| 4 | `4_guards_challenge` | Guards: challenge | challenge | DONE |
| 5 | `5_session_auth` | SessionAuth | tutorial | DONE |
| 6 | `6_jwt_auth` | JWTAuth и JWTCookieAuth | tutorial | DONE |
| 7 | `7_oauth2_password` | OAuth2PasswordBearerAuth | tutorial | DONE |
| 8 | `8_auth_bugfix` | Security backends: найди ошибки | bugfix | DONE |
| 9 | `9_exclude_include` | Excluding/including endpoints from auth | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/security/

**Ключевые концепции:**
- Guard functions, накопление guards по слоям App -> Router -> Handler
- `AbstractAuthenticationMiddleware`, `AuthenticationResult`
- `SessionAuth`, `JWTAuth`, `JWTCookieAuth`, `OAuth2PasswordBearerAuth`
- `exclude`/`exclude_opt_key` для публичных эндпоинтов

---

## Том 4 — Данные & Хранение

> Key-value stores, кэширование, ORM, миграции.
> **Зависимости:** Том 3

### Глава 4.1 — Stores & Caching (6 уроков) — 5 DONE + 1 NEW

Хранилища, кэширование ответов, rate limiting, серверные сессии, Redis/Valkey.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_memory_store` | MemoryStore и StoreRegistry | tutorial | DONE |
| 2 | `2_response_cache` | Response Cache | tutorial | DONE |
| 3 | `3_rate_limiting` | Rate Limiting | tutorial | DONE |
| 4 | `4_sessions` | Серверные сессии | tutorial | DONE |
| 5 | `5_redis_store` | Redis/Valkey Store | tutorial | DONE |
| 6 | `6_stores_challenge` | Stores: реализуй кэширование + rate limiting | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/stores/ , https://docs.litestar.dev/latest/usage/caching/

---

### Глава 4.2 — Databases: SQLAlchemy (7 уроков) — NEW

SQLAlchemy plugin, init plugin, repository pattern, интеграция с DTO, Dishka, миграции.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_sa_plugin` | SQLAlchemy Plugin: сериализация моделей | tutorial | **NEW** |
| 2 | `2_sa_init` | SQLAlchemy Init Plugin: engine, sessions | tutorial | **NEW** |
| 3 | `3_sa_repository` | SQLAlchemy Repository: CRUD | tutorial | **NEW** |
| 4 | `4_sa_dto` | SQLAlchemy + DTO | tutorial | **NEW** |
| 5 | `5_sa_dishka` | SQLAlchemy + Dishka: production DI | tutorial | **NEW** |
| 6 | `6_sa_challenge` | SQLAlchemy: реализуй CRUD API | challenge | **NEW** |
| 7 | `7_alembic_setup` | Alembic: миграции БД | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/databases/sqlalchemy/

**Ключевые концепции:**
- `SQLAlchemyPlugin`, `SQLAlchemyInitPlugin`, `SQLAlchemyAsyncConfig`
- `SQLAlchemyAsyncRepository`, `SQLAlchemyDTO`
- Engine/session lifecycle, transaction management
- Интеграция с Dishka: session-scoped providers
- Alembic: async конфигурация, autogenerate, работа с SQLAlchemyAsyncConfig

---

## Том 5 — Frontend & Realtime

> Серверный рендеринг, статика, WebSockets, HTMX.
> **Зависимости:** Том 1 (routing, responses). Не требует Том 3.

### Глава 5.1 — Templates & Static Files (5 уроков) — NEW

Jinja2, статические файлы, HTML-режим.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_jinja_basics` | Jinja2: TemplateEngine, Template response | tutorial | **NEW** |
| 2 | `2_template_context` | Context, callables, custom functions | tutorial | **NEW** |
| 3 | `3_static_files` | StaticFilesConfig | tutorial | **NEW** |
| 4 | `4_html_mode` | HTML-first handlers (media_type=HTML) | tutorial | **NEW** |
| 5 | `5_templates_challenge` | Templates: собери страницу с динамическими данными | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/templating/ , https://docs.litestar.dev/latest/usage/static-files/

---

### Глава 5.2 — WebSockets (6 уроков) — NEW

Low-level WS, listeners, streaming, Channels (pub/sub), аутентификация в WS.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_ws_low_level` | Low-level websocket handler | tutorial | **NEW** |
| 2 | `2_ws_listener` | websocket_listener и WebSocketListener | tutorial | **NEW** |
| 3 | `3_ws_stream` | websocket_stream | tutorial | **NEW** |
| 4 | `4_channels` | Channels: pub/sub с WebSocket | tutorial | **NEW** |
| 5 | `5_ws_auth` | Аутентификация в WebSocket | tutorial | **NEW** |
| 6 | `6_ws_challenge` | WebSockets: реализуй чат | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/websockets/ , https://docs.litestar.dev/latest/usage/channels/

**Почему WS-аутентификация:**
Браузерное API WebSocket не поддерживает кастомные HTTP-заголовки. Bearer token через Authorization header не сработает. Урок показывает паттерны: token в query-param при подключении, ticket-based authentication через первое сообщение.

---

### Глава 5.3 — HTMX Integration (4 урока) — NEW

Litestar HTMX plugin для динамических server-rendered интерфейсов.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_htmx_basics` | HTMXRequest, HX-headers, partial responses | tutorial | **NEW** |
| 2 | `2_htmx_crud` | HTMX CRUD: hx-get/hx-post/hx-swap | tutorial | **NEW** |
| 3 | `3_htmx_sse` | HTMX + SSE: live updates | tutorial | **NEW** |
| 4 | `4_htmx_challenge` | HTMX: собери интерактивный список | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/htmx/

**Зависимости:** Глава 5.1 (Templates)

---

## Том 6 — Интеграции & Production

> Eventing, message brokers, продвинутое тестирование, наблюдаемость, продвинутые паттерны.
> **Зависимости:** Тома 1-4

### Глава 6.1 — Events (3 урока) — NEW

Async event system.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_event_listener` | EventListener: подписка на именованные события | tutorial | **NEW** |
| 2 | `2_event_emitter` | SimpleEventEmitter: отправка из хендлеров | tutorial | **NEW** |
| 3 | `3_events_challenge` | Events: реализуй notification pipeline | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/events/

---

### Глава 6.2 — FastStream Integration (4 урока) — NEW

Message brokers через FastStream, интеграция с Litestar.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_faststream_basics` | FastStream: pub/sub с RabbitMQ | tutorial | **NEW** |
| 2 | `2_litestar_integration` | FastStream + Litestar: shared app | tutorial | **NEW** |
| 3 | `3_testing_streams` | Тестирование stream handlers | tutorial | **NEW** |
| 4 | `4_faststream_challenge` | FastStream: реализуй event-driven pipeline | challenge | **NEW** |

**Docs:** https://faststream.airt.ai/latest/

**Зависимости:** Том 0 (инфраструктура: RabbitMQ), Том 3 (DI)

---

### Глава 6.3 — Advanced Testing (2 урока) — NEW

Dependency override, мокинг сервисов и брокеров.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_dependency_override` | Переопределение зависимостей в тестах | tutorial | **NEW** |
| 2 | `2_testing_challenge` | Testing: напиши тесты для API с моками | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/testing/

**Базовый TestClient — в Главе 2.4.** Здесь только продвинутые паттерны: override dependencies, mock DI providers, тестирование auth flows.

---

### Глава 6.4 — Observability (4 урока) — NEW

Логирование, метрики, tracing.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_logging` | LoggingMiddlewareConfig: structured logging | tutorial | **NEW** |
| 2 | `2_prometheus` | Prometheus plugin: /metrics endpoint | tutorial | **NEW** |
| 3 | `3_opentelemetry` | OpenTelemetry plugin: tracing | tutorial | **NEW** |
| 4 | `4_structlog` | Structlog integration | tutorial | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/metrics/

---

### Глава 6.5 — Advanced Patterns (7 уроков) — NEW

Plugins, пагинация, type encoders, специализированные хуки.

| # | ID | Название | Mode | Статус |
|---|-----|----------|------|--------|
| 1 | `1_plugins` | InitPluginProtocol, SerializationPluginProtocol | tutorial | **NEW** |
| 2 | `2_pagination` | ClassicPagination, CursorPagination, OffsetPagination | tutorial | **NEW** |
| 3 | `3_type_encoders` | Кастомная сериализация: datetime, Decimal, UUID | tutorial | **NEW** |
| 4 | `4_before_send` | before_send hook: response wrapping, correlation ID | tutorial | **NEW** |
| 5 | `5_problem_details` | Problem Details plugin (RFC 9457) | tutorial | **NEW** |
| 6 | `6_flash_messages` | Flash Messages plugin | tutorial | **NEW** |
| 7 | `7_advanced_challenge` | Advanced: paginated API с custom encoders | challenge | **NEW** |

**Docs:** https://docs.litestar.dev/latest/usage/plugins/

---

## Roadmap

### Phase 1 — Заполнение пробелов (приоритет: высокий, 10 уроков)

Новые уроки для существующих + перенесённых глав.

| # | Урок | Глава | Mode | Описание |
|---|------|-------|------|----------|
| 1 | `6_dto_challenge` | 2.3 DTO | challenge | CRUD с write/read DTO |
| 2 | `7_dto_bugfix` | 2.3 DTO | bugfix | Типичные ошибки в DTO конфигурации |
| 3 | `7_allowed_hosts` | 3.2 Middleware | tutorial | AllowedHostsMiddleware |
| 4 | `9_exclude_include` | 3.3 Security | tutorial | exclude/exclude_opt_key для auth |
| 5 | `6_stores_challenge` | 4.1 Stores | challenge | Кэширование + rate limiting |
| 6 | `6_background_tasks` | 1.4 Responses | tutorial | BackgroundTask/BackgroundTasks |
| 7 | `1_test_client` | 2.4 Testing | tutorial | Синхронный TestClient |
| 8 | `2_async_test_client` | 2.4 Testing | tutorial | AsyncTestClient |
| 9 | `1_pydantic_settings` | 2.5 Config | tutorial | pydantic-settings + .env |

**9 новых уроков + 1 новая глава (2.4) + 1 новая глава (2.5)**

### Phase 2 — Core New Content (приоритет: высокий, 7 уроков)

| Глава | Уроков |
|-------|--------|
| 4.2 Databases: SQLAlchemy | 7 (включая Alembic) |

**7 новых уроков**

### Phase 3 — Frontend & Realtime (приоритет: средний, 15 уроков)

| Глава | Уроков |
|-------|--------|
| 5.1 Templates & Static Files | 5 |
| 5.2 WebSockets | 6 (включая WS auth) |
| 5.3 HTMX Integration | 4 |

**15 новых уроков**

### Phase 4 — Integrations & Production (приоритет: низкий, 20 уроков)

| Глава | Уроков |
|-------|--------|
| 6.1 Events | 3 |
| 6.2 FastStream | 4 |
| 6.3 Advanced Testing | 2 |
| 6.4 Observability | 4 |
| 6.5 Advanced Patterns | 7 |

**20 новых уроков**

---

## Кандидаты на будущее (за рамками v5)

| Тема | Описание | Приоритет |
|------|----------|-----------|
| Messaging (отдельная глава) | Выделить очереди сообщений в отдельную главу | Средний |
| Deferred Tasks (SAQ) | Litestar-SAQ: отложенные задачи | Средний |
| GraphQL (Strawberry) | Strawberry integration для GraphQL | Средний |
| Granian | Альтернативный ASGI сервер на Rust | Средний |
| Piccolo ORM | Альтернативный ORM с плагином | Низкий |
| TypedDict as schema | TypedDict вместо dataclass/pydantic | Низкий |
| on_app_init hooks | Хуки инициализации приложения | Низкий |
| Content negotiation deep dive | Accept, q-values, multiple representations | Низкий |
| AttrsDTO | attrs/cattrs через плагин | Низкий |
| File system abstraction | S3/GCS/local через единый API | Низкий |

---
