# S1T Litestar Workbench

Интерактивная платформа для изучения Litestar framework.

## Запуск

### Локально

```bash
uv sync
s1t-litestar
```

Платформа: http://localhost:8000

### Docker Compose

```bash
docker compose up --build
```

Сервис,URL,Доступ
Platform,http://localhost:8000,—
RabbitMQ UI,http://localhost:15672,guest / guest
RedisInsight,http://localhost:5540,redis://valkey:6379 (совместимо с Valkey)
pgAdmin 4,http://localhost:5050,admin@local.dev / admin
PostgreSQL,localhost:5432,postgres / postgres / learn_litestar
Valkey,localhost:6379,—
RabbitMQ AMQP,localhost:5672,—

Postgres в pgAdmin добавлен автоматически — сервер `learn_litestar` уже настроен.

## Переменные окружения

Все переменные с префиксом `S1T_` переопределяют `app/config.py`:

Переменная,Описание,По умолчанию
S1T_PORT,Порт платформы,8000
S1T_DEBUG,Debug-режим,false
S1T_LESSON_PORT,Порт lesson-серверов,8200

В Docker-окружении lesson-серверы дополнительно получают:

VALKEY_URL — valkey://valkey:6379

RABBITMQ_URL — amqp://guest:guest@rabbitmq:5672/

DATABASE_URL — postgresql://postgres:postgres@postgres:5432/learn_litestar


"Hey @Maintainers (или конкретным активным админам)!
I've been building a comprehensive, interactive learning platform for Litestar. It's designed to be run locally so users can solve coding challenges right in their environment, though I've also deployed a read-only showcase here: [Ссылка].
Source code: [Ссылка на GitHub].

I built this because I love the framework and wanted to make the onboarding process easier for newcomers. I'd love to get your feedback! Also, if you think this is valuable for the community, would you be open to adding it to the official Litestar documentation/ecosystem page?"
