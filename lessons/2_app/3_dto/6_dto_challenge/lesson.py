from litestar import Litestar
import logger_setup

from models import Product, _store, next_id

# TODO: создай ProductWriteDTO (DataclassDTO[Product])
#   exclude: id, created_at, internal_cost

# TODO: создай ProductReadDTO (DataclassDTO[Product])
#   exclude: internal_cost

# TODO: создай ProductPatchDTO (DataclassDTO[Product])
#   exclude: id, created_at, internal_cost
#   partial=True

# TODO: реализуй POST /products (status 201)
#   dto=ProductWriteDTO, return_dto=ProductReadDTO
#   data: DTOData[Product] → data.create_instance(id=next_id())

# TODO: реализуй GET /products/{product_id:int}
#   return_dto=ProductReadDTO
#   возвращает NotFoundException если нет

# TODO: реализуй PATCH /products/{product_id:int}
#   dto=ProductPatchDTO, return_dto=ProductReadDTO
#   data.update_instance(product)
#   возвращает NotFoundException если нет

# TODO: реализуй GET /products
#   return_dto=ProductReadDTO
#   возвращает list[Product]

app = Litestar(route_handlers=[])
#                               ^ добавь свои хендлеры сюда
