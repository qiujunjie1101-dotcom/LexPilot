"""节点：审计意见书归档、Trace 保存与任务完结。"""
from __future__ import annotations

from typing import Any

from ...services import audit_service
from ..state import ReviewState


def finalize(state: ReviewState) -> dict[str, Any]:
    audit_service.audit(
        state['context'],
        state['contract_id'],
        'contract_review',
        {'review_id': state['review_id'], 'risk_level': state['risk_level'], 'risk_score': state['risk_score']},
        state['trace_id'],
    )
    summary = dict(state['summary'])
    summary.update({
        'review_id': state['review_id'],
        'trace_id': state['trace_id'],
        'status': state['status'],
        'legal_review_id': state.get('legal_review_id'),
    })
    return {'summary': summary}
