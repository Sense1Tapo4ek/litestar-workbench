import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

from loguru import logger

from ..models import ProcessInfo, ServerStatus

_HEALTHCHECK_TIMEOUT = 10.0
_HEALTHCHECK_INTERVAL = 0.3
_STOP_WAIT = 3.0


class ProcessManager:
    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        self._processes: dict[str, ProcessInfo] = {}
        self._log_queues: dict[str, list[asyncio.Queue]] = {}

    def _key(self, volume_id: str, chapter_id: str, lesson_id: str) -> str:
        return f"{volume_id}/{chapter_id}/{lesson_id}"

    def get_running_lesson(self) -> tuple[str, str, str] | None:
        """Return (volume_id, chapter_id, lesson_id) of the running server, or None."""
        for key, info in self._processes.items():
            if info.process.returncode is None and info.status == ServerStatus.RUNNING:
                parts = key.split("/", 2)
                return parts[0], parts[1], parts[2]
        return None

    def get_status(self, volume_id: str, chapter_id: str, lesson_id: str) -> ServerStatus:
        info = self._processes.get(self._key(volume_id, chapter_id, lesson_id))
        if info is None:
            return ServerStatus.STOPPED
        if info.process.returncode is not None:
            return ServerStatus.STOPPED
        return info.status

    def get_log_buffer(self, volume_id: str, chapter_id: str, lesson_id: str) -> list[str]:
        info = self._processes.get(self._key(volume_id, chapter_id, lesson_id))
        return list(info.log_buffer) if info else []

    async def start(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        port: int,
        cwd: Path | None = None,
    ) -> ServerStatus:
        key = self._key(volume_id, chapter_id, lesson_id)
        if key in self._processes:
            info = self._processes[key]
            if info.process.returncode is None and info.status == ServerStatus.RUNNING:
                return ServerStatus.RUNNING
            await self._kill_process(key)

        # Enforce single-server policy: block if a different lesson is already running
        running = self.get_running_lesson()
        if running is not None and self._key(*running) != key:
            logger.warning(
                f"Cannot start {key}: server {self._key(*running)} is already running"
            )
            return ServerStatus.CONFLICT

        lesson_dir = cwd or (
            self._project_root / "lessons" / volume_id / chapter_id / lesson_id
        )
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "lesson:app",
            "--port",
            str(port),
            "--host",
            "0.0.0.0",
            "--log-level",
            "info",
        ]
        logger.info(f"Starting lesson server: {' '.join(cmd)} (cwd={lesson_dir})")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(lesson_dir),
        )

        info = ProcessInfo(
            process=process,
            port=port,
            status=ServerStatus.STARTING,
            started_at=datetime.now(),
        )
        self._processes[key] = info
        # Preserve existing SSE subscriber queues — do NOT reset them.
        self._log_queues.setdefault(key, [])

        asyncio.create_task(self._read_logs(key, process))

        try:
            await asyncio.wait_for(
                self._healthcheck(port), timeout=_HEALTHCHECK_TIMEOUT
            )
            info.status = ServerStatus.RUNNING
            logger.info(f"Lesson server running on port {port}")
        except asyncio.TimeoutError:
            logger.warning(f"Healthcheck timed out for port {port}")
            info.status = ServerStatus.STOPPED

        return info.status

    async def stop(self, volume_id: str, chapter_id: str, lesson_id: str) -> None:
        key = self._key(volume_id, chapter_id, lesson_id)
        if key not in self._processes:
            return
        info = self._processes[key]
        info.status = ServerStatus.STOPPING
        info.log_buffer.clear()
        await self._kill_process(key)

    async def stop_all(self) -> None:
        for key in list(self._processes.keys()):
            await self._kill_process(key)

    async def stream_logs(
        self, volume_id: str, chapter_id: str, lesson_id: str
    ) -> AsyncGenerator[str, None]:
        key = self._key(volume_id, chapter_id, lesson_id)

        # yield buffered logs first
        info = self._processes.get(key)
        if info:
            for line in info.log_buffer:
                yield line

        # subscribe to new logs via queue
        q: asyncio.Queue[str | None] = asyncio.Queue()
        self._log_queues.setdefault(key, []).append(q)
        try:
            while True:
                line = await q.get()
                if line is None:
                    break
                yield line
        finally:
            queues = self._log_queues.get(key, [])
            if q in queues:
                queues.remove(q)

    async def _healthcheck(self, port: int) -> None:
        while True:
            try:
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                writer.close()
                await writer.wait_closed()
                return
            except OSError:
                await asyncio.sleep(_HEALTHCHECK_INTERVAL)

    async def _read_logs(self, key: str, process: asyncio.subprocess.Process) -> None:
        assert process.stdout is not None
        while True:
            try:
                raw = await process.stdout.readline()
            except Exception:
                break
            if not raw:
                break
            line = raw.decode(errors="replace").rstrip()
            info = self._processes.get(key)
            if info:
                info.log_buffer.append(line)
            for q in self._log_queues.get(key, []):
                await q.put(line)

        # Do NOT send None sentinel: keep SSE connections alive so they
        # automatically receive logs from the next server start.

    async def _kill_process(self, key: str) -> None:
        info = self._processes.pop(key, None)
        if info is None:
            return
        try:
            info.process.terminate()
            try:
                await asyncio.wait_for(info.process.wait(), timeout=_STOP_WAIT)
            except asyncio.TimeoutError:
                info.process.kill()
                await info.process.wait()
        except ProcessLookupError:
            pass
        logger.info(f"Stopped lesson server: {key}")
