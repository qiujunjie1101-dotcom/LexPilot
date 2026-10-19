"""合规审计日志仓储。"""
from __future__ import annotations

from typing import Any

from ..database import execute


class AuditRepository:
    def add(self, values: tuple[Any, ...]) -> None:
        execute(
            'INSERT INTO audit_logs(trace_id,contract_id,actor_id,action,detail_json,created_at) VALUES (?,?,?,?,?,?)',
            values,
        )


audit_repository = AuditRepository()
