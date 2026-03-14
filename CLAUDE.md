# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Commands

```bash
uv sync                                                        # Install dependencies
uv run uvicorn app.main:app --port 8000 --reload --app-dir src # Run platform (dev)
s1t-litestar                                                   # Run platform (after uv sync)
docker compose up -d                                           # Full stack: all infra services
npm run build:editor --prefix src/ui                           # Rebuild CodeMirror bundle
```

`S1T_DEBUG=true` and other `S1T_*` env vars override defaults in `src/app/config.py`. No tests.

---

## Infrastructure

All services are defined in `docker-compose.yml`. In Docker, they communicate by service name.

| Service      | Port(s)       | UI / Access                                      |
|--------------|---------------|--------------------------------------------------|
| platform     | 8000          | http://localhost:8000                            |
| postgres     | 5432          | user: postgres / pass: postgres / db: learn_litestar |
| valkey       | 6379          | Redis-compatible (Valkey)                        |
| rabbitmq     | 5672, 15672   | AMQP + Management UI: http://localhost:15672 (guest/guest) |
| pgadmin      | 5050          | http://localhost:5050 (admin@local.dev / admin)  |
| redisinsight | 5540          | http://localhost:5540                            |

**`DATABASE_URL`** is set in `docker-compose.yml` environment but is NOT in `LearningConfig` — lesson servers read it directly from the process environment.

Env vars for platform services (set in docker-compose or locally):
- `S1T_VALKEY_URL` — default `valkey://localhost:6379`
- `S1T_RABBITMQ_URL` — default `amqp://guest:guest@localhost:5672/`

---

## Architecture

**S1T Litestar Workbench** — interactive learning platform. Two distinct runtimes:

1. **Platform** (`src/app/`) — Litestar + Jinja2 + HTMX. Manages UI, file editing, lesson server lifecycle.
2. **Lesson servers** (`lessons/`) — each lesson is a self-contained Litestar app (`lesson.py`) run by uvicorn as a subprocess. Only one can run at a time (`ServerStatus.CONFLICT` returned otherwise).

### Service layer (`src/app/services/`)

All services are provided via **Dishka DI** (`LearningProvider` in `src/app/provider.py`, `Scope.APP`):

- **`scanner.py`** (`LessonScanner`) — discovers `lessons/` at startup, reads `volume.yaml` / `chapter.yaml` / `lesson.yaml` / `lesson.md` / `scenario.yaml`. Key methods: `scan()`, `get_lesson_files_raw()`, `get_theory_html(lang)`, `get_scenario()`. `lesson.md` supports `<!-- lang: xx -->` markers for language sections.
- **`process_manager.py`** (`ProcessManager`) — asyncio subprocess lifecycle; 500-line log ring buffer per lesson; TCP healthcheck (10s timeout). SSE log stream at `/api/server/{ch}/{ls}/logs`.
- **`workspace.py`** (`WorkspaceManager`) — copy-on-write isolation. Original files in `lessons/` are never modified. First save copies `.py` files to `.workspaces/{ch}/{ls}/`. Key: `get_active_dir()`, `save_file()`, `reset_workspace()`.
- **`executor.py`** (`ScenarioExecutor`) — runs scenario steps: HTTP (`httpx`), WebSocket (`websockets`), FastStream (`aio_pika` → RabbitMQ). Supports `${var.field}` interpolation from `save_as` step results.
- **`log_streamer.py`** — formats SSE log entries as HTML `<div class="log-entry log-{level}">`. Classifies ERROR/CRITICAL, WARNING, DEBUG, INFO.

### DI and config

**`src/app/provider.py`** — `LearningProvider(Provider)` with `Scope.APP`. Provides: `LearningConfig`, `LessonScanner`, `ProcessManager` (async, cleanup on shutdown), `ScenarioExecutor`, `WorkspaceManager`.

**`src/app/config.py`** — `LearningConfig(BaseSettings)`, env prefix `S1T_`:

| Field          | Default                              |
|----------------|--------------------------------------|
| `host`         | `0.0.0.0`                            |
| `port`         | `8000`                               |
| `debug`        | `false`                              |
| `lessons_dir`  | `lessons`                            |
| `lesson_port`  | `8200`                               |
| `workspace_dir`| `.workspaces`                        |
| `valkey_url`   | `valkey://localhost:6379`            |
| `rabbitmq_url` | `amqp://guest:guest@localhost:5672/` |

### Request flow (scenario step execution)

```
Browser (HTMX hx-post) → POST /api/scenario/{ch}/{ls}/{step_id}/execute
    → ScenarioApiController.execute_step()
    → ScenarioExecutor.execute_step(step, port=8200)
    → HTTP:       httpx → http://127.0.0.1:8200{path}
    → WebSocket:  websockets → ws://127.0.0.1:8200{path}
    → FastStream: aio_pika → rabbitmq_url (publish/subscribe)
    → Returns step_result.html partial (HTMX swap)
```

---

## Lesson format

**Volume**: each volume directory has `volume.yaml` with fields: `order`, `title_ru`, `title_en`, `description_ru`, `description_en`, `summary_ru`, `summary_en`.

**Chapter**: each chapter directory has `chapter.yaml` with fields: `order`, `title_ru`, `title_en`, `description_ru`, `description_en`.

**Lesson**: each lesson directory:

| File           | Required | Purpose |
|----------------|----------|---------|
| `lesson.yaml`  | YES      | `title_ru`, `title_en`, `order` (float), `mode: tutorial\|challenge\|bugfix` |
| `lesson.py`    | YES      | `app = Litestar(...)`. No module-level docstring. |
| `lesson.md`    | no       | Theory content with `<!-- lang: ru -->` / `<!-- lang: en -->` markers. Rendered to HTML (Markdown + Pygments). Single file consolidates both languages. |
| `scenario.yaml`| no       | Test steps (HTTP / websocket / faststream) |
| extra `.py`    | no       | Shown as additional editor tabs |

### Lesson modes

| Mode        | Badge       | Behavior |
|-------------|-------------|----------|
| `tutorial`  | —           | Code works. Read theory, run scenario. |
| `challenge` | `CHALLENGE` | Skeleton with `# TODO`. Implement so all steps pass. |
| `bugfix`    | `BUGFIX`    | Intentional errors. Find and fix them. |

---

## Chapters

### Chapter 0 — Platform Guide (`lessons/0_platform/`)
How to use S1T Litestar Workbench: editor, server controls, scenario runner, lesson modes.

Lessons (7):
- `1_welcome` — Welcome
- `2_about` — О платформе и курсе
- `3_http` — HTTP: Заголовки и Куки (cookies, headers)
- `4_ws` — WebSockets
- `5_infra` — Внешние сервисы (RabbitMQ, Valkey, PostgreSQL)
- `6_challenge` — пример урока типа challenge
- `7_bugfix` — пример урока типа bugfix

### Chapter 1 — Основы (`lessons/1_basics/`)
Routes, controllers, routers, query params, request body, special request params,
responses, error handling, State, lifecycle hooks, OpenAPI, CLI.
- Docs: https://docs.litestar.dev/latest/

Lessons (24): hello_world, routing functions/bugfix/advanced/opt_name/challenge, controllers/bugfix,
routers, query params/challenge, request body/challenge, request special, responses basic/bugfix/advanced,
error handling/challenge, state/bugfix, lifecycle, openapi, cli.

### Chapter 2 — DTO (`lessons/2_dto/`)
DataclassDTO, PydanticDTO, MsgspecDTO, Write/Read DTO, DTOData + PATCH.
- Docs: https://docs.litestar.dev/latest/usage/dto/

Patterns: `data.create_instance(**extra)` (POST), `data.update_instance(obj)` (PATCH), `DTOConfig(partial=True)`.
Never use `body: {}` in scenario.yaml — executor skips empty dict bodies.

### Chapter 3 — Dependency Injection (`lessons/3_di/`)
Layered architecture, built-in DI (`Provide`, `Dependency`, generator deps), Dishka (basics,
inject, providers, scopes, testing, UoW pattern).
- Docs (Litestar DI): https://docs.litestar.dev/latest/usage/dependency-injection/
- Docs (Dishka): https://dishka.readthedocs.io/

Key patterns: `@get` on top, `@inject` below. `FromDishka[T]` type hint. `override=True` for provider override.
Guards accumulate (all run), dependencies override (nearest wins), response_headers merge.

### Chapter 5 — Stores & Caching (`lessons/5_stores/`)
MemoryStore, response cache, rate limiting, server-side sessions, Redis/Valkey store.
- Docs: https://docs.litestar.dev/latest/usage/stores/
- RedisInsight: http://localhost:5540
- RabbitMQ Management: http://localhost:15672
- pgAdmin: http://localhost:5050

---

## Scenario YAML: step types

### HTTP (default)
```yaml
steps:
  - name: "Create item"
    method: POST
    path: /items
    body: {"name": "test"}
    expect_status: 201
    save_as: item          # stores full JSON response
  - name: "Get item"
    method: GET
    path: /items/${item.id}  # ${save_as_name.field} interpolation
    expect_status: 200
```

### WebSocket
```yaml
  - name: "Echo"
    type: websocket
    path: /ws
    messages:
      - send: '{"text": "hello"}'
        expect_contains: "hello"
```

### FastStream (RabbitMQ)
```yaml
  - name: "Publish event"
    type: faststream
    stream_messages:
      - topic: orders
        payload: {"id": 1}
        expect_topic: order_created
        expect_contains: "processed"
```

---

## Frontend

- **Templates**: `src/ui/templates/` — `base.html`, `home.html`, `lesson.html`, `partials/`
- **Static**: `src/ui/static/js/`, `src/ui/static/css/`
- **CodeMirror 6** — `cm-entry.js` → `cm-bundle.js` (esbuild). Initialized in `editor.js` (ES module). Ctrl+S saves; auto-save after 1.5s debounce. Auto-restart lesson server on save if running.
- **HTMX 2.0.4** — partial updates (server controls, step results, Run All progress)
- **SSE** — log streaming via `hx-ext="sse"` → `/api/server/{ch}/{ls}/logs`
- **`websocket.js`** — browser WS client, rendered in `ws_panel.html`
- **CSS** — Japandi design system (`variables.css`). Accents: Sage `#62996A`, Mustard `#DFA842`, Terracotta `#BA574A`, Lavender `#9584C9`. Text scale: `--text-primary` → `--text-muted` (lightest).

Partials in `src/ui/templates/partials/`: `server_controls.html`, `step_card.html`, `step_result.html`, `all_results.html`, `lesson_list.html`, `code_tab.html`, `ws_panel.html`. `step_result.html` and `all_results.html` both render `StepResult` — keep in sync.

---

## Key models

**`src/app/models/chapter.py`**
- `LessonMode` (StrEnum): `TUTORIAL / CHALLENGE / BUGFIX`
- `ServerStatus` (StrEnum): `stopped / starting / running / stopping / conflict`
- `Lesson`, `Chapter`, `LessonFile`, `ProcessInfo` (log_buffer: deque maxlen=500)

**`src/app/models/scenario.py`**
- `StepType` (StrEnum): `HTTP / WEBSOCKET / FASTSTREAM`
- `StepResult` — `step_id, actual_status, elapsed_ms, passed, response_body, error, step_type, response_headers: dict[str,str], response_cookies`
- `WebSocketMessage` — `send, expect, expect_contains`
- `FastStreamMessage` — `topic, payload, expect_topic, expect_contains`
- `ScenarioStep`, `ScenarioLink`, `Scenario`

---

## Workspace and port

- Lesson server always binds to `settings.lesson_port` (default 8200, override `S1T_LESSON_PORT`)
- `WorkspaceManager.get_active_dir()` → workspace path if exists, else original lesson dir
- Reset = delete `.workspaces/{ch}/{ls}/`, server restarts in original dir
- One lesson server at a time — `ServerStatus.CONFLICT` if another is already running
