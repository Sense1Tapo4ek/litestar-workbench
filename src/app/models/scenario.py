from dataclasses import dataclass, field
from enum import StrEnum


class StepType(StrEnum):
    HTTP = "http"
    WEBSOCKET = "websocket"
    FASTSTREAM = "faststream"


@dataclass
class WebSocketMessage:
    send: str
    expect: str | None = None
    expect_contains: str | None = None


@dataclass
class FastStreamMessage:
    topic: str
    payload: str
    expect_topic: str | None = None
    expect_contains: str | None = None


@dataclass
class ScenarioStep:
    id: int
    name: str
    method: str
    path: str
    expect_status: int
    description: str = ""
    body: dict | None = None
    save_as: str | None = None
    step_type: StepType = StepType.HTTP
    messages: list[WebSocketMessage] | None = None
    stream_messages: list[FastStreamMessage] | None = None
    cookies: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    save_cookies: str | None = None


@dataclass
class ScenarioLink:
    name: str
    url: str
    icon: str = ""


@dataclass
class Scenario:
    steps: list[ScenarioStep] = field(default_factory=list)
    links: list[ScenarioLink] = field(default_factory=list)


@dataclass
class StepResult:
    step_id: int
    actual_status: int
    elapsed_ms: float
    passed: bool
    response_body: str | None = None
    error: str | None = None
    step_type: StepType = StepType.HTTP
    response_headers: dict[str, str] = field(default_factory=dict)
    response_cookies: dict[str, str] = field(default_factory=dict)
