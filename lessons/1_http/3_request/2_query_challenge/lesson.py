
from litestar import Litestar
import logger_setup


_products = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 999.0},
    {"id": 2, "name": "Book", "category": "education", "price": 29.0},
    {"id": 3, "name": "Phone", "category": "electronics", "price": 699.0},
    {"id": 4, "name": "Desk", "category": "furniture", "price": 249.0},
    {"id": 5, "name": "Lamp", "category": "furniture", "price": 45.0},
]


# TODO: реализуй GET /products/search
# Параметры:
#   - q: str (обязательный) — фильтр по подстроке в name (без учёта регистра)
#   - category: str | None (опциональный, дефолт None) — фильтр по category
#   - min_price: float (опциональный, дефолт 0.0, ge=0)
#   - max_price: float (опциональный, дефолт 10000.0, le=100000)
#   - limit: int (опциональный, дефолт 10, ge=1, le=50)
# Возвращает: {"results": [...], "count": N, "query": q}


# TODO: реализуй GET /products/{product_id:int}
# Возвращает продукт по id или {"error": "not found"} с кодом 404


app = Litestar(route_handlers=[])
#                               ^ добавь хендлеры сюда
