"""节点：多维度加权风险综合计分与定级。"""
from __future__ import annotations

from typing import Any

from ...services import risk_service
from ..state import ReviewState


def assess(state: ReviewState) -> dict[str, Any]:
    score = risk_service.score(state['issues'])
    level = risk_service.level(score, state['issues'])
    return {
        'risk_score': score,
        'risk_level': level,
        'legal_review_required': risk_service.legal_review_required(level, state['issues']),
    }
