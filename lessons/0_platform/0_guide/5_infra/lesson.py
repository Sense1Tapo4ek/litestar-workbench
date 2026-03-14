import asyncpg
import valkey.asyncio as aivalkey
from aio_pika import connect_robust
from litestar import Litestar, get
from litestar.exceptions import HTTPException

from infra_config import infra
from logger_setup import logger


@get("/valkey")
async def check_valkey() -> dict:
    logger.info("Valkey check")
    try:
        client = aivalkey.from_url(infra.valkey_url)
        await client.ping()
        await client.aclose()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Valkey unavailable: {e}")
    return {"valkey": "ok", "url": infra.valkey_url}


@get("/rabbitmq")
async def check_rabbitmq() -> dict:
    logger.info("RabbitMQ check")
    try:
        conn = await connect_robust(infra.rabbitmq_url)
        await conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RabbitMQ unavailable: {e}")
    return {"rabbitmq": "ok", "url": infra.rabbitmq_url}


@get("/postgres")
async def check_postgres() -> dict:
    logger.info("PostgreSQL check")
    try:
        conn = await asyncpg.connect(infra.database_url)
        await conn.close()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"PostgreSQL unavailable: {e}")
    return {"postgres": "ok", "database": "learn_litestar"}


app = Litestar([check_valkey, check_rabbitmq, check_postgres])
