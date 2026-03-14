# Руководство по созданию уроков — S1T Litestar Workbench

---

## Структура директорий

```
lessons/
├── 1_basics/                        # глава
│   ├── _meta.yaml                   # метаданные главы (обязательно)
│   ├── 1_hello_world/               # урок
│   │   ├── lesson.yaml              # метаданные урока (обязательно)
│   │   ├── lesson.py                # Litestar-приложение (обязательно)
│   │   ├── lesson.md                # теория (опционально)
│   │   ├── scenario.yaml            # тест-сценарий (опционально)
│   │   └── models.py                # доп. файлы кода (опционально)
│   └── 2_lifecycle/
│       └── ...
└── 2_routing/
    └── ...
```

**Правила именования:**
- Глава и урок — директории без пробелов, обычно с префиксом-номером: `1_basics`, `2_hello_world`
- Директории, начинающиеся с `_`, сканером игнорируются
- Урок обнаруживается только если в нём есть `lesson.py`

---

## Файлы главы

### `_meta.yaml` — обязательный

```yaml
title: "Основы"
order: 1
```

| Поле | Тип | Описание |
|------|-----|----------|
| `title` | string | Название главы в интерфейсе |
| `order` | int | Порядок сортировки глав |

---

## Файлы урока

### `lesson.yaml` — обязательный

```yaml
title: Hello World
order: 1
mode: tutorial
```

| Поле | Тип | По умолчанию | Описание |
|------|-----|------|----------|
| `title` | string | — | Название урока |
| `order` | int | — | Порядок внутри главы |
| `mode` | string | `tutorial` | Режим: `tutorial`, `challenge`, `bugfix` |

**Режимы:**

| Режим | Когда использовать |
|-------|--------------------|
| `tutorial` | Объяснительный урок — студент читает теорию и изучает код |
| `challenge` | Студент пишет код, чтобы пройти тесты |
| `bugfix` | В коде намеренно допущены ошибки — нужно найти и исправить |

---

### `lesson.py` — обязательный

Главное требование: экспортировать объект `app = Litestar(...)`.

```python
from litestar import Litestar, get

@get("/")
async def index() -> dict:
    return {"message": "Hello from Litestar!"}

app = Litestar(route_handlers=[index])
```

**Важно:**
- Файл **не должен** иметь модульный docstring (первая строка не должна быть строкой-документацией)
- Объект приложения должен называться именно `app`
- Все хендлеры должны быть `async def` с аннотациями типов

---

### `lesson.md` — опциональный

Теоретический контент в Markdown. Поддерживает расширенный синтаксис.

```markdown
# Роутинг в Litestar

Litestar использует декораторы для каждого HTTP-метода.

## Пример

```python
from litestar import get, post

@get("/items")
async def list_items() -> list[dict]:
    return []
```

Посмотрите [реализацию](code:lesson.py#L5) в редакторе.

| Декоратор | Метод  |
|-----------|--------|
| `@get`    | GET    |
| `@post`   | POST   |
| `@put`    | PUT    |
| `@patch`  | PATCH  |
| `@delete` | DELETE |
```

**Специальные ссылки:**

| Синтаксис | Действие |
|-----------|----------|
| `[текст](code:lesson.py)` | Открывает файл в редакторе |
| `[текст](code:lesson.py#L10)` | Открывает файл и переходит на строку 10 |

---

### `scenario.yaml` — опциональный

Описывает последовательность тестовых шагов. Поддерживает HTTP и WebSocket.

```yaml
steps:
  - ...          # список шагов (см. ниже)

links:
  - ...          # ссылки в панели сервера (опционально)
```

---

## Типы шагов сценария

### HTTP-шаг (по умолчанию)

```yaml
steps:
  - name: "Создать элемент"
    method: POST
    path: /items
    body:
      name: "Чистый код"
      price: 29.99
    expect_status: 201
    description: "POST /items — создаёт новый элемент"
    save_as: item
```

| Поле | Тип | По умолчанию | Описание |
|------|-----|------|----------|
| `name` | string | — | Название шага в интерфейсе |
| `method` | string | `GET` | HTTP-метод |
| `path` | string | `/` | URL-путь, поддерживает `${переменная}` |
| `body` | dict | — | JSON-тело запроса |
| `expect_status` | int | `200` | Ожидаемый HTTP-статус |
| `description` | string | `""` | Описание шага |
| `save_as` | string | — | Имя переменной для сохранения ответа |
| `type` | string | `http` | Тип шага (можно не указывать) |

---

### WebSocket-шаг

```yaml
steps:
  - name: "Эхо-тест"
    type: websocket
    path: /ws
    messages:
      - send: '{"text": "hello"}'
        expect_contains: "hello"
      - send: '{"text": "world"}'
        expect: '{"echo": "world"}'
```

| Поле | Тип | Описание |
|------|-----|----------|
| `type` | string | Обязательно `websocket` |
| `path` | string | Путь WebSocket-эндпоинта |
| `messages` | list | Список сообщений |

**Поля сообщения:**

| Поле | Описание |
|------|----------|
| `send` | Строка, отправляемая на сервер |
| `expect` | Точное совпадение ответа |
| `expect_contains` | Ответ должен содержать эту подстроку |

`expect` и `expect_contains` — взаимоисключающие, используйте одно из двух.

---

### Переменные между шагами

Ответ шага с `save_as` доступен в последующих шагах через `${имя.поле}`.

```yaml
steps:
  - name: "Создать"
    method: POST
    path: /items
    body: {name: "Книга", price: 10}
    expect_status: 201
    save_as: item            # сохраняем ответ как 'item'

  - name: "Прочитать"
    method: GET
    path: "/items/${item.id}"   # item.id — поле из сохранённого ответа
    expect_status: 200

  - name: "Удалить"
    method: DELETE
    path: "/items/${item.id}"
    expect_status: 204
```

**Синтаксис:**
- `${item}` — весь сохранённый объект
- `${item.id}` — поле `id` из объекта
- `${item.nested.field}` — вложенное поле

---

### Ссылки в панели сервера

```yaml
links:
  - name: "Swagger UI"
    url: "/schema/swagger"
  - name: "OpenAPI JSON"
    url: "/schema/openapi.json"
```

Ссылки отображаются в правой панели рядом со стандартными кнопками ReDoc, Swagger и т.д.

---

## Дополнительные файлы кода

Все `.py`-файлы кроме `__init__.py` автоматически появляются в редакторе как вкладки.

```
lesson.py       # всегда первая вкладка
models.py       # следующие — в алфавитном порядке
database.py
utils.py
```

Импортировать их из `lesson.py` можно напрямую:

```python
from models import Item, create_item
from database import get_db
```

---

## Полный пример: challenge-урок

### Структура

```
lessons/2_crud/1_items_api/
├── lesson.yaml
├── lesson.py
├── models.py
├── lesson.md
└── scenario.yaml
```

### `lesson.yaml`

```yaml
title: Items API
order: 1
mode: challenge
```

### `models.py`

```python
from dataclasses import dataclass

_store: dict[int, "Item"] = {}
_next_id = 1


@dataclass
class Item:
    name: str
    price: float
    id: int | None = None


def create_item(name: str, price: float) -> Item:
    global _next_id
    item = Item(id=_next_id, name=name, price=price)
    _store[_next_id] = item
    _next_id += 1
    return item


def get_item(item_id: int) -> Item | None:
    return _store.get(item_id)


def list_items() -> list[Item]:
    return list(_store.values())


def delete_item(item_id: int) -> bool:
    return _store.pop(item_id, None) is not None
```

### `lesson.py`

```python
from litestar import Litestar, delete, get, post
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from models import Item, create_item, delete_item, get_item, list_items


@get("/items")
async def get_items() -> list[Item]:
    return list_items()


@post("/items", status_code=HTTP_201_CREATED)
async def create_new_item(data: Item) -> Item:
    return create_item(name=data.name, price=data.price)


@get("/items/{item_id:int}")
async def get_one_item(item_id: int) -> Item:
    item = get_item(item_id)
    if item is None:
        raise NotFoundException(f"Item {item_id} not found")
    return item


@delete("/items/{item_id:int}", status_code=HTTP_204_NO_CONTENT)
async def delete_one_item(item_id: int) -> None:
    if not delete_item(item_id):
        raise NotFoundException(f"Item {item_id} not found")


app = Litestar(route_handlers=[get_items, create_new_item, get_one_item, delete_one_item])
```

### `lesson.md`

```markdown
# Items API

Реализуйте CRUD-эндпоинты для ресурса `Item`.

## Задание

Модели и хранилище уже написаны в [models.py](code:models.py).
Реализуйте хендлеры в [lesson.py](code:lesson.py).

## Ожидаемые эндпоинты

| Метод  | Путь              | Статус | Описание         |
|--------|-------------------|--------|------------------|
| GET    | `/items`          | 200    | Список элементов |
| POST   | `/items`          | 201    | Создать элемент  |
| GET    | `/items/{id:int}` | 200    | Получить по ID   |
| DELETE | `/items/{id:int}` | 204    | Удалить по ID    |

## Подсказка

Используйте `NotFoundException` для случаев, когда элемент не найден:

```python
from litestar.exceptions import NotFoundException

raise NotFoundException(f"Item {item_id} not found")
```
```

### `scenario.yaml`

```yaml
steps:
  - name: "Пустой список"
    method: GET
    path: /items
    expect_status: 200
    description: "GET /items возвращает пустой массив"

  - name: "Создать элемент"
    method: POST
    path: /items
    body:
      name: "Чистый код"
      price: 29.99
    expect_status: 201
    description: "POST /items создаёт элемент"
    save_as: item

  - name: "Получить по ID"
    method: GET
    path: "/items/${item.id}"
    expect_status: 200

  - name: "Несуществующий ID"
    method: GET
    path: /items/9999
    expect_status: 404
    description: "Несуществующий элемент → 404"

  - name: "Удалить"
    method: DELETE
    path: "/items/${item.id}"
    expect_status: 204

  - name: "Подтвердить удаление"
    method: GET
    path: "/items/${item.id}"
    expect_status: 404
```

---

## Чек-лист нового урока

- [ ] Создана директория `lessons/<глава>/<урок>/`
- [ ] `lesson.yaml` содержит `title` и `order`
- [ ] `lesson.py` экспортирует `app = Litestar(...)`
- [ ] `lesson.py` не имеет модульного docstring
- [ ] Все хендлеры — `async def` с аннотациями типов
- [ ] `lesson.md` содержит теорию (для tutorial/challenge)
- [ ] `scenario.yaml` написан и шаги проверены (для challenge/bugfix)
- [ ] Урок запускается через кнопку Start без ошибок
- [ ] Все шаги сценария проходят при правильном коде
