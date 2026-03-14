from litestar import Litestar
import logger_setup



# TODO: напиши обработчик для ValueError -- возвращает {"error": str(exc)} с кодом 400


# TODO: реализуй GET /orders/{order_id:int}
#   - если заказ не найден -> NotFoundException


# TODO: реализуй POST /orders
#   - принимает data: dict с полями item и amount
#   - если data["amount"] <= 0 -> raise ValueError("Amount must be positive")
#   - иначе -> создаёт заказ, возвращает 201


app = Litestar(
    route_handlers=[],
    exception_handlers={},
    #                       ^ добавь обработчик ValueError
)
