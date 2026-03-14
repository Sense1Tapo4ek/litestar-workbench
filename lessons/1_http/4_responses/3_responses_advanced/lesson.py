import asyncio
from pathlib import Path

from litestar import Litestar, get
from litestar.response import File, Stream

from logger_setup import logger


@get("/stream")
async def stream_numbers() -> Stream:
    logger.info("stream_numbers: 5 chunks")
    async def generator():
        for i in range(5):
            await asyncio.sleep(0.05)
            yield f"chunk-{i}\n".encode()

    return Stream(generator())


@get("/download")
async def download_file() -> File:
    logger.info("download_file: export.txt")
    return File(
        path=Path(__file__).parent / "sample.txt",
        filename="export.txt",
    )


app = Litestar(route_handlers=[stream_numbers, download_file])
