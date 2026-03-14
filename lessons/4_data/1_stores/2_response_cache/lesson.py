from litestar import Litestar, Request, get
from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.memory import MemoryStore

from logger_setup import logger

_compute_calls = 0
_lang_calls = 0


@get("/compute", cache=5)
async def compute() -> dict:
    global _compute_calls
    _compute_calls += 1
    logger.info(f"compute() called (count={_compute_calls})")
    return {"result": _compute_calls * 10, "call_count": _compute_calls}


@get("/calls")
async def call_counts() -> dict:
    return {"compute_calls": _compute_calls, "lang_calls": _lang_calls}


def key_by_lang(request: Request) -> str:
    return f"greeting:{request.query_params.get('lang', 'en')}"


@get("/greeting", cache=60, cache_key_builder=key_by_lang)
async def greeting(lang: str = "en") -> dict:
    global _lang_calls
    _lang_calls += 1
    logger.info(f"greeting({lang}) called (count={_lang_calls})")
    translations = {"en": "Hello", "es": "Hola", "fr": "Bonjour"}
    return {
        "lang": lang,
        "text": translations.get(lang, "?"),
        "call_count": _lang_calls,
    }


app = Litestar(
    route_handlers=[compute, call_counts, greeting],
    stores={"response_cache": MemoryStore()},
    response_cache_config=ResponseCacheConfig(store="response_cache"),
)
