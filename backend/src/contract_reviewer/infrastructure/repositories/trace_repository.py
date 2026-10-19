"""全链路 Trace 事件仓储。"""
from __future__ import annotations

from typing import Any

from ..database import execute, rows


class TraceRepository:
    def add(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO trace_events(trace_id,node,detail_json,latency_ms,created_at) VALUES (?,?,?,?,?)', values)

    def list_by_trace(self, trace_id: str) -> list[dict[str, Any]]:
        return rows(
            'SELECT id,trace_id,node,detail_json,latency_ms,created_at FROM trace_events WHERE trace_id=? ORDER BY id',
            (trace_id,),
        )


trace_repository = TraceRepository()
