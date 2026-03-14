from litestar import get, Litestar
import logger_setup


# TODO: раскомментируй оба хендлера

# @get("/hello")
# async def hello() -> dict:
#     return {"message": "Hello, World!"}


# @get("/greet/{name:str}")
# async def greet(name: str) -> dict:
#     return {"greeting": f"Hello, {name}!"}


app = Litestar(route_handlers=[greet, hello])
