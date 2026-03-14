from litestar import Litestar
import logger_setup


_books: dict[int, dict] = {
    1: {"id": 1, "title": "Clean Code", "author": "Robert Martin"},
    2: {"id": 2, "title": "Refactoring", "author": "Martin Fowler"},
    3: {"id": 3, "title": "Design Patterns", "author": "GoF"},
}


# TODO: реализуй GET /books -- возвращает list[dict] всех книг


# TODO: реализуй GET /books/{book_id:int} -- возвращает dict или 404


# TODO: реализуй GET /books/{book_id:int}/chapters/{chapter_num:int}
# Если книга с book_id не найдена — NotFoundException (404)
# Иначе возвращает {"book_id": book_id, "chapter": chapter_num}
# Главы не хранятся отдельно — достаточно вернуть оба параметра из пути


# TODO: реализуй DELETE /books/{book_id:int} -- удаляет книгу, возвращает 204 или 404


app = Litestar(route_handlers=[])
#                               ^ добавь хендлеры сюда
