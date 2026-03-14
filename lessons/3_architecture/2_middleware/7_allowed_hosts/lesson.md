<!-- lang: ru -->
# AllowedHostsMiddleware

`AllowedHostsConfig` защищает приложение от **Host header injection** атак — когда злоумышленник подделывает заголовок `Host` в запросе.

```python
from litestar.config.allowed_hosts import AllowedHostsConfig

app = Litestar(
    allowed_hosts=AllowedHostsConfig(
        allowed_hosts=["example.com", "api.example.com"],
        www_redirect=True,   # example.com → www.example.com
    )
)
```

Запросы с неизвестным `Host` получают **400 Bad Request**.

**`www_redirect=True`** — автоматически перенаправляет `example.com` → `www.example.com`.

**Wildcard:** `"*.example.com"` разрешает все поддомены.

**Для локальной разработки** добавь `"localhost"`, `"127.0.0.1"`, `"testserver"` в список.

<!-- lang: en -->
# AllowedHostsMiddleware

`AllowedHostsConfig` protects against **Host header injection** attacks — where an attacker forges the `Host` header in the request.

```python
from litestar.config.allowed_hosts import AllowedHostsConfig

app = Litestar(
    allowed_hosts=AllowedHostsConfig(
        allowed_hosts=["example.com", "api.example.com"],
        www_redirect=True,   # example.com → www.example.com
    )
)
```

Requests with unknown `Host` get **400 Bad Request**.

**`www_redirect=True`** — automatically redirects `example.com` → `www.example.com`.

**Wildcard:** `"*.example.com"` allows all subdomains.

**For local development** add `"localhost"`, `"127.0.0.1"`, `"testserver"` to the list.
