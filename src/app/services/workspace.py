import shutil
from pathlib import Path

from loguru import logger


class WorkspaceManager:
    def __init__(self, workspace_dir: Path, lessons_dir: Path) -> None:
        self._workspace_dir = workspace_dir
        self._lessons_dir = lessons_dir

    def _ws_path(self, volume_id: str, chapter_id: str, lesson_id: str) -> Path:
        return self._workspace_dir / volume_id / chapter_id / lesson_id

    def _lesson_path(self, volume_id: str, chapter_id: str, lesson_id: str) -> Path:
        return self._lessons_dir / volume_id / chapter_id / lesson_id

    def ensure_workspace(self, volume_id: str, chapter_id: str, lesson_id: str) -> Path:
        ws = self._ws_path(volume_id, chapter_id, lesson_id)
        if ws.exists():
            return ws
        ws.mkdir(parents=True, exist_ok=True)
        lesson_dir = self._lesson_path(volume_id, chapter_id, lesson_id)
        for py_file in lesson_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            shutil.copy2(py_file, ws / py_file.name)
        logger.info(f"Created workspace for {volume_id}/{chapter_id}/{lesson_id}")
        return ws

    def get_active_dir(self, volume_id: str, chapter_id: str, lesson_id: str) -> Path:
        ws = self._ws_path(volume_id, chapter_id, lesson_id)
        if ws.exists():
            return ws
        return self._lesson_path(volume_id, chapter_id, lesson_id)

    def save_file(
        self, volume_id: str, chapter_id: str, lesson_id: str, filename: str, content: str
    ) -> None:
        ws = self.ensure_workspace(volume_id, chapter_id, lesson_id)
        (ws / filename).write_text(content)

    def read_file(
        self, volume_id: str, chapter_id: str, lesson_id: str, filename: str
    ) -> str:
        active = self.get_active_dir(volume_id, chapter_id, lesson_id)
        return (active / filename).read_text()

    def reset_workspace(self, volume_id: str, chapter_id: str, lesson_id: str) -> None:
        ws = self._ws_path(volume_id, chapter_id, lesson_id)
        if ws.exists():
            shutil.rmtree(ws)
            logger.info(f"Reset workspace for {volume_id}/{chapter_id}/{lesson_id}")

    def has_modifications(self, volume_id: str, chapter_id: str, lesson_id: str) -> bool:
        return self._ws_path(volume_id, chapter_id, lesson_id).exists()

    def is_file_modified(
        self, volume_id: str, chapter_id: str, lesson_id: str, filename: str
    ) -> bool:
        ws = self._ws_path(volume_id, chapter_id, lesson_id)
        if not ws.exists():
            return False
        ws_file = ws / filename
        if not ws_file.exists():
            return False
        original = self._lesson_path(volume_id, chapter_id, lesson_id) / filename
        if not original.exists():
            return True
        return ws_file.read_text() != original.read_text()
