import logging
import sys
from datetime import datetime

import structlog


def _timestamper(_, __, event_dict):
    now = datetime.now()
    event_dict["timestamp"] = f"{now:%H:%M:%S}.{now.microsecond // 1000:03d}"
    return event_dict


def _renderer(_, __, event_dict):
    ts = event_dict.pop("timestamp", "")
    level = event_dict.pop("level", "info").upper()
    event = event_dict.pop("event", "")
    return f"{ts} {level:<8} {event}"


_pre_chain = [structlog.stdlib.add_log_level, _timestamper]

structlog.configure(
    processors=[*_pre_chain, _renderer],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

_formatter = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        _renderer,
    ],
    foreign_pre_chain=_pre_chain,
)

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(_formatter)

for _name in (None, "uvicorn", "uvicorn.error", "uvicorn.access"):
    _lg = logging.getLogger(_name)
    _lg.handlers = [_handler]
    _lg.setLevel(logging.DEBUG if _name is None else logging.INFO)
    if _name:
        _lg.propagate = False

logger = structlog.get_logger()
