"""节点：条款与企业标准模板基线的字段级差异比对。"""
from __future__ import annotations

from time import perf_counter
from typing import Any

from ...services import audit_service
from ...services.clause_diff_service import diff_clause
from ..state import ReviewState


def run(state: ReviewState, clause: dict[str, Any]) -> dict[str, Any]:
    started = perf_counter()
    diff = diff_clause(clause, state['template'].get(clause['clause_type']))
    audit_service.trace(state['trace_id'], 'clause_diff', diff, started)
    return diff
