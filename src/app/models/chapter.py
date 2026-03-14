import asyncio
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum


class ServerStatus(StrEnum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CONFLICT = "conflict"


class LessonMode(StrEnum):
    TUTORIAL = "tutorial"
    CHALLENGE = "challenge"
    BUGFIX = "bugfix"


@dataclass
class Lesson:
    id: str          # "1_hello_world"
    title_ru: str
    title_en: str
    order: int
    port: int        # 8200
    volume_id: str   # "1_http"
    chapter_id: str  # "1_routing"
    files: list[str]
    has_scenario: bool
    mode: LessonMode = LessonMode.TUTORIAL

    @property
    def title(self) -> str:
        return self.title_ru


@dataclass
class Chapter:
    id: str          # "1_routing"
    title_ru: str
    title_en: str
    order: int
    description_ru: str
    description_en: str
    volume_id: str   # "1_http"
    lessons: list[Lesson] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.title_ru

    @property
    def description(self) -> str:
        return self.description_ru


@dataclass
class Volume:
    id: str          # "1_http"
    title_ru: str
    title_en: str
    order: int
    description_ru: str
    description_en: str
    summary_ru: str = ""
    summary_en: str = ""
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.title_ru

    @property
    def description(self) -> str:
        return self.description_ru

    @property
    def lesson_count(self) -> int:
        return sum(len(ch.lessons) for ch in self.chapters)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)


@dataclass
class LessonFile:
    filename: str
    content: str
    highlighted_html: str
    line_count: int


@dataclass
class ProcessInfo:
    process: asyncio.subprocess.Process
    port: int
    status: ServerStatus
    started_at: datetime
    log_buffer: deque[str] = field(default_factory=lambda: deque(maxlen=500))
