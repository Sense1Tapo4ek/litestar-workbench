from dataclasses import dataclass
from typing import Annotated

from litestar import Litestar, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.datastructures import UploadFile
from litestar.status_codes import HTTP_201_CREATED

from logger_setup import logger


@dataclass
class Product:
    name: str
    price: float
    tags: list[str] | None = None


@post("/products", status_code=HTTP_201_CREATED)
async def create_product(data: Product) -> dict:
    logger.info(f"create_product: {data.name} price={data.price}")
    return {"name": data.name, "price": data.price, "tags": data.tags or []}


@post("/contact")
async def contact_form(
    data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)],
) -> dict:
    logger.info(f"contact_form: {list(data.keys())}")
    return {"received": True, "fields": list(data.keys())}


@post("/upload")
async def upload_file(
    data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
) -> dict:
    content = await data.read()
    logger.info(f"upload_file: {data.filename} {len(content)}b")
    return {"filename": data.filename, "size": len(content)}


app = Litestar(route_handlers=[create_product, contact_form, upload_file])
