"""节点：结合审查上下文生成初审意见与修订建议。"""
from __future__ import annotations

from time import perf_counter
from typing import Any

from ...services import audit_service, llm_service
from ..state import ReviewState


def generate(state: ReviewState) -> dict[str, Any]:
    started = perf_counter()
    recommendation = llm_service.recommendation(state['contract'], state['issues'], state['evidence'])
    audit_service.trace(state['trace_id'], 'recommendation', recommendation, started)
    return {'recommendation': recommendation}
