from litestar import Litestar, Request, get, post, delete
from litestar.config.csrf import CSRFConfig

from logger_setup import logger

_notes: dict[int, dict] = {
    1: {"id": 1, "text": "Первая заметка"},
    2: {"id": 2, "text": "Вторая заметка"},
}
_counter = 2


@get("/notes")
async def list_notes() -> list[dict]:
    logger.info(f"list_notes: count={len(_notes)}")
    return list(_notes.values())


@get("/csrf-token")
async def get_csrf_token(request: Request) -> dict[str, str]:
    token = request.cookies.get("csrftoken", "not-set")
    logger.info("get_csrf_token: returning token from cookie")
    return {"csrf_token": token}


@post("/notes")
async def create_note(data: dict[str, str]) -> dict:
    global _counter
    _counter += 1
    note = {"id": _counter, "text": data["text"]}
    _notes[_counter] = note
    logger.info(f"create_note: id={_counter}")
    return note


@delete("/notes/{note_id:int}")
async def delete_note(note_id: int) -> None:
    logger.info(f"delete_note: id={note_id}")
    _notes.pop(note_id, None)


csrf_config = CSRFConfig(
    secret="s1t-csrf-secret-key-change-in-production",
    cookie_name="csrftoken",
    header_name="x-csrftoken",
)

app = Litestar(
    route_handlers=[list_notes, get_csrf_token, create_note, delete_note],
    csrf_config=csrf_config,
)
