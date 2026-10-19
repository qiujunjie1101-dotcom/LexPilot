"""结构化日志配置与链路追踪 ID 注入。"""
from __future__ import annotations

import contextvars
import json
import logging
import sys
from datetime import datetime, timezone

_trace_id: contextvars.ContextVar[str] = contextvars.ContextVar('trace_id', default='-')


def set_trace_id(trace_id: str) -> None:
    _trace_id.set(trace_id)


def get_trace_id() -> str:
    return _trace_id.get()


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'time': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'trace_id': get_trace_id(),
            'message': record.getMessage(),
        }
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
