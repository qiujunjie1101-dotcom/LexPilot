"""条件路由边逻辑：增量跳过、人审阻断等判定。"""
from __future__ import annotations

from typing import Any

from .state import ReviewState


def should_review_clause(state: ReviewState, clause: dict[str, Any]) -> bool:
    return clause['clause_type'] in state['changed_clause_types']


def requires_legal_review(state: ReviewState) -> bool:
    return bool(state.get('legal_review_required'))
