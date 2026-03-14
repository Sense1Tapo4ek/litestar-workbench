<!-- lang: ru -->
# Конфигурация через pydantic-settings

`pydantic-settings` позволяет читать конфигурацию из переменных окружения и `.env` файлов с валидацией типов.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",   # APP_DEBUG, APP_SECRET_KEY, ...
        env_file=".env",
    )

    app_name: str = "My App"
    debug: bool = False
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./dev.db"

settings = AppConfig()
```

**Приоритет источников** (от высшего к низшему):
1. Переменные окружения (`APP_DEBUG=true`)
2. `.env` файл
3. Дефолтные значения

**`.env` файл:**
```
APP_APP_NAME=Production App
APP_DEBUG=false
APP_SECRET_KEY=super-secret-key-here
APP_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

> **Двойной префикс:** поле `app_name` + префикс `APP_` = переменная `APP_APP_NAME`. Pydantic-settings объединяет префикс и имя поля.

**Правило:** никогда не хардкоди секреты (`secret_key`, пароли, API ключи) в коде. Используй переменные окружения.

<!-- lang: en -->
# Configuration with pydantic-settings

`pydantic-settings` reads configuration from environment variables and `.env` files with type validation.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",   # APP_DEBUG, APP_SECRET_KEY, ...
        env_file=".env",
    )

    app_name: str = "My App"
    debug: bool = False
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./dev.db"

settings = AppConfig()
```

**Source priority** (highest to lowest):
1. Environment variables (`APP_DEBUG=true`)
2. `.env` file
3. Default values

**`.env` file:**
```
APP_APP_NAME=Production App
APP_DEBUG=false
APP_SECRET_KEY=super-secret-key-here
APP_DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

> **Double prefix:** field `app_name` + prefix `APP_` = env var `APP_APP_NAME`. Pydantic-settings concatenates the prefix with the field name.

**Rule:** never hardcode secrets (`secret_key`, passwords, API keys) in code. Use environment variables.
