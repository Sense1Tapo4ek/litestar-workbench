from pathlib import Path

import re
from typing import Literal

import markdown
import yaml
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

from ..models import (
    Chapter,
    Lesson,
    LessonFile,
    LessonMode,
    Volume,
    FastStreamMessage,
    Scenario,
    ScenarioLink,
    ScenarioStep,
    StepType,
    WebSocketMessage,
)

_MD_EXTENSIONS = [
    "tables",
    "pymdownx.highlight",
    "pymdownx.superfences",
    "pymdownx.inlinehilite",
    "pymdownx.tasklist",
    "admonition",
    "attr_list",
]

_MD_EXTENSION_CONFIGS = {
    "pymdownx.highlight": {
        "use_pygments": True,
        "noclasses": False,
        "css_class": "highlight",
    },
}

_PYGMENTS_FORMATTER = HtmlFormatter(
    linenos="table",
    cssclass="highlight",
    wrapcode=False,
)


class LessonScanner:
    def __init__(self, lessons_dir: Path, lesson_port: int) -> None:
        self.lessons_dir = lessons_dir
        self.lesson_port = lesson_port

    def scan(self) -> list[Volume]:
        volumes: list[Volume] = []
        if not self.lessons_dir.exists():
            return volumes

        for vol_dir in sorted(self.lessons_dir.iterdir()):
            if not vol_dir.is_dir() or vol_dir.name.startswith("_"):
                continue
            vol_meta_file = vol_dir / "volume.yaml"
            if not vol_meta_file.exists():
                continue

            vol_meta = yaml.safe_load(vol_meta_file.read_text()) or {}
            volume = Volume(
                id=vol_dir.name,
                title_ru=vol_meta.get("title_ru", vol_dir.name),
                title_en=vol_meta.get("title_en", vol_meta.get("title_ru", vol_dir.name)),
                order=vol_meta.get("order", 999),
                description_ru=vol_meta.get("description_ru", ""),
                description_en=vol_meta.get("description_en", vol_meta.get("description_ru", "")),
                summary_ru=vol_meta.get("summary_ru", vol_meta.get("description_ru", "")),
                summary_en=vol_meta.get("summary_en", vol_meta.get("summary_ru", vol_meta.get("description_en", vol_meta.get("description_ru", "")))),
            )

            for ch_dir in sorted(vol_dir.iterdir()):
                if not ch_dir.is_dir() or ch_dir.name.startswith("_"):
                    continue
                ch_meta_file = ch_dir / "chapter.yaml"
                if not ch_meta_file.exists():
                    continue

                ch_meta = yaml.safe_load(ch_meta_file.read_text()) or {}
                chapter = Chapter(
                    id=ch_dir.name,
                    title_ru=ch_meta.get("title_ru", ch_dir.name),
                    title_en=ch_meta.get("title_en", ch_meta.get("title_ru", ch_dir.name)),
                    order=ch_meta.get("order", 999),
                    description_ru=ch_meta.get("description_ru", ""),
                    description_en=ch_meta.get("description_en", ch_meta.get("description_ru", "")),
                    volume_id=volume.id,
                )

                for lesson_dir in sorted(ch_dir.iterdir()):
                    if not lesson_dir.is_dir() or lesson_dir.name.startswith("_"):
                        continue
                    lesson_file = lesson_dir / "lesson.py"
                    if not lesson_file.exists():
                        continue

                    meta_file = lesson_dir / "lesson.yaml"
                    meta_data = (
                        yaml.safe_load(meta_file.read_text()) or {} if meta_file.exists() else {}
                    )

                    py_files = sorted(
                        [
                            f.name
                            for f in lesson_dir.glob("*.py")
                            if f.name != "__init__.py"
                        ],
                        key=lambda n: (0 if n == "lesson.py" else 1, n),
                    )

                    raw_mode = meta_data.get("mode", "tutorial")
                    try:
                        mode = LessonMode(raw_mode)
                    except ValueError:
                        mode = LessonMode.TUTORIAL

                    lesson = Lesson(
                        id=lesson_dir.name,
                        title_ru=meta_data.get("title_ru", lesson_dir.name),
                        title_en=meta_data.get("title_en", meta_data.get("title_ru", lesson_dir.name)),
                        order=meta_data.get("order", 999),
                        port=self.lesson_port,
                        volume_id=volume.id,
                        chapter_id=chapter.id,
                        files=py_files,
                        has_scenario=(lesson_dir / "scenario.yaml").exists(),
                        mode=mode,
                    )
                    chapter.lessons.append(lesson)

                chapter.lessons.sort(key=lambda l: l.order)
                volume.chapters.append(chapter)

            volume.chapters.sort(key=lambda c: c.order)
            volumes.append(volume)

        volumes.sort(key=lambda v: v.order)
        return volumes

    def _lesson_path(self, volume_id: str, chapter_id: str, lesson_id: str) -> Path:
        return self.lessons_dir / volume_id / chapter_id / lesson_id

    def get_lesson_files(
        self, volume_id: str, chapter_id: str, lesson_id: str
    ) -> list[LessonFile]:
        lesson_dir = self._lesson_path(volume_id, chapter_id, lesson_id)
        py_files = sorted(
            [f for f in lesson_dir.glob("*.py") if f.name != "__init__.py"],
            key=lambda f: (0 if f.name == "lesson.py" else 1, f.name),
        )
        result = []
        for py_file in py_files:
            content = py_file.read_text()
            highlighted = highlight(content, PythonLexer(), _PYGMENTS_FORMATTER)
            result.append(
                LessonFile(
                    filename=py_file.name,
                    content=content,
                    highlighted_html=highlighted,
                    line_count=content.count("\n") + 1,
                )
            )
        return result

    def get_lesson_files_raw(
        self,
        volume_id: str,
        chapter_id: str,
        lesson_id: str,
        source_dir: Path | None = None,
    ) -> dict[str, str]:
        d = source_dir or self._lesson_path(volume_id, chapter_id, lesson_id)
        py_files = sorted(
            [f for f in d.glob("*.py") if f.name != "__init__.py"],
            key=lambda f: (0 if f.name == "lesson.py" else 1, f.name),
        )
        return {f.name: f.read_text() for f in py_files}

    def get_theory_html(
        self, volume_id: str, chapter_id: str, lesson_id: str, lang: Literal["ru", "en"] = "ru"
    ) -> str | None:
        """Returns rendered HTML for lesson.md content in specified language.

        Parses <!-- lang: xx --> markers to extract language sections.
        Returns entire content as-is if no markers found (backward compat).
        Falls back to other language if requested language missing.
        Returns None if file does not exist.
        """
        md_file = self._lesson_path(volume_id, chapter_id, lesson_id) / "lesson.md"
        if not md_file.exists():
            return None

        md_text = md_file.read_text()
        sections = self._parse_lang_sections(md_text)

        # If no language sections found, return entire content
        if not sections:
            return markdown.markdown(
                md_text,
                extensions=_MD_EXTENSIONS,
                extension_configs=_MD_EXTENSION_CONFIGS,
            )

        # Try requested language first, then fallback
        content = sections.get(lang)
        if content is None:
            # Fallback to other language
            other_lang = "en" if lang == "ru" else "ru"
            content = sections.get(other_lang)

        if content is None:
            return None

        return markdown.markdown(
            content,
            extensions=_MD_EXTENSIONS,
            extension_configs=_MD_EXTENSION_CONFIGS,
        )

    def _parse_lang_sections(self, content: str) -> dict[str, str]:
        """Parse <!-- lang: xx --> markers and return dict of language sections.

        Pattern: re.split(r"^<!-- lang: (\\w+) -->\\s*$", content, flags=re.MULTILINE)
        Result: [preamble, lang1, content1, lang2, content2, ...]
        Returns dict with lang as key; preamble is discarded.
        """
        parts = re.split(r"^<!-- lang: (\w+) -->\s*$", content, flags=re.MULTILINE)
        if len(parts) <= 1:
            # No markers found
            return {}

        sections = {}
        # parts[0] is preamble (discarded)
        # Iterate pairs: (lang, content, lang, content, ...)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                lang = parts[i]
                text = parts[i + 1].lstrip("\n")  # Remove leading newline after marker
                sections[lang] = text

        return sections

    def get_scenario(
        self, volume_id: str, chapter_id: str, lesson_id: str
    ) -> Scenario | None:
        yaml_file = self._lesson_path(volume_id, chapter_id, lesson_id) / "scenario.yaml"
        if not yaml_file.exists():
            return None
        data = yaml.safe_load(yaml_file.read_text())
        steps = []
        for i, s in enumerate(data.get("steps", [])):
            raw_type = s.get("type", "http").lower()
            try:
                step_type = StepType(raw_type)
            except ValueError:
                step_type = StepType.HTTP

            messages = None
            if step_type == StepType.WEBSOCKET and s.get("messages"):
                messages = [
                    WebSocketMessage(
                        send=m.get("send", ""),
                        expect=m.get("expect"),
                        expect_contains=m.get("expect_contains"),
                    )
                    for m in s["messages"]
                ]

            stream_messages = None
            if step_type == StepType.FASTSTREAM and s.get("messages"):
                stream_messages = [
                    FastStreamMessage(
                        topic=m.get("topic", ""),
                        payload=m.get("payload", ""),
                        expect_topic=m.get("expect_topic"),
                        expect_contains=m.get("expect_contains"),
                    )
                    for m in s["messages"]
                ]

            steps.append(
                ScenarioStep(
                    id=i,
                    name=s.get("name", f"Step {i}"),
                    method=s.get("method", "GET").upper(),
                    path=s.get("path", "/"),
                    body=s.get("body"),
                    expect_status=s.get("expect_status", 200),
                    description=s.get("description", ""),
                    save_as=s.get("save_as"),
                    step_type=step_type,
                    messages=messages,
                    stream_messages=stream_messages,
                    cookies=s.get("cookies"),
                    headers=s.get("headers"),
                    save_cookies=s.get("save_cookies"),
                )
            )
        links = [
            ScenarioLink(
                name=lnk.get("name", ""),
                url=lnk.get("url", "/"),
                icon=lnk.get("icon", ""),
            )
            for lnk in data.get("links", [])
        ]
        return Scenario(steps=steps, links=links)
