"""全链路 Trace 追踪与合规审计日志记录服务。"""
from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from ..common.logger import get_logger
from ..common.security import SecurityContext
from ..infrastructure.database import jdump, jload
from ..infrastructure.repositories.audit_repository import audit_repository
from ..infrastructure.repositories.trace_repository import trace_repository

logger = get_logger(__name__)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_trace_id() -> str:
    return f'trace-{uuid.uuid4().hex[:12]}'


def trace(trace_id: str, node: str, detail: dict[str, Any], started: float) -> None:
    latency_ms = int((time.perf_counter() - started) * 1000)
    trace_repository.add((trace_id, node, jdump(detail), latency_ms, utcnow()))
    logger.debug('node=%s trace_id=%s latency_ms=%s', node, trace_id, latency_ms)


def audit(ctx: SecurityContext, contract_id: str, action: str, detail: dict[str, Any], trace_id: str | None = None) -> None:
    audit_repository.add((trace_id, contract_id, ctx.user_id, action, jdump(detail), utcnow()))


def list_traces(trace_id: str) -> list[dict[str, Any]]:
    data = trace_repository.list_by_trace(trace_id)
    for item in data:
        item['detail'] = jload(item.pop('detail_json'), {})
    return data
