from litestar import Controller, Litestar, delete, get, post
from litestar.exceptions import NotFoundException
from litestar.status_codes import HTTP_201_CREATED
import logger_setup


_notes: dict[int, dict] = {}
_next_id = 1


class NoteController(Controller):
    path = "/notes"
    tags = ["notes"]

    @get()
    async def list_notes(self) -> list[dict]:
        return list(_notes.values())

    @post(status_code=HTTP_201_CREATED)
    async def create_note(self, data: dict) -> dict:
        global _next_id
        note = {"id": _next_id, **data}
        _notes[_next_id] = note
        _next_id += 1
        return note

    @get("/{note_id:int}")
    async def get_note(self, id: int) -> dict:
        note = _notes.get(id)
        if note is None:
            raise NotFoundException(detail=f"Note {id} not found")
        return note

    @delete("/{note_id:int}", status_code=200)
    async def delete_note(self, note_id: int) -> dict:
        note = _notes.pop(note_id, None)
        if note is None:
            raise NotFoundException(detail=f"Note {note_id} not found")
        return {"deleted": True}


app = Litestar(route_handlers=[NoteController()])
