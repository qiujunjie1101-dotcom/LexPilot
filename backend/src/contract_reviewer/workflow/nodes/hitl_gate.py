"""节点：高危风险人工复核阻断门禁（触发人审断点）。"""
from __future__ import annotations

import uuid
from typing import Any

from ...common.constants import REVIEW_STATUS_PRECHECK_PASSED, REVIEW_STATUS_WAITING_LEGAL
from ...infrastructure.database import jdump
from ...infrastructure.repositories.review_repository import review_repository
from ...services import audit_service, report_service
from .. import edges
from ..checkpointer import checkpointer
from ..state import ReviewState


def gate(state: ReviewState) -> dict[str, Any]:
    contract = state['contract']
    legal_required = edges.requires_legal_review(state)
    status = REVIEW_STATUS_WAITING_LEGAL if legal_required else REVIEW_STATUS_PRECHECK_PASSED
    summary = report_service.build_summary(
        contract,
        state['diffs'],
        state['issues'],
        state['evidence'],
        state['reviewed_clause_types'],
        state['changed_clause_types'],
        state['risk_score'],
        state['risk_level'],
        legal_required,
        state['recommendation'],
    )
    review_id = f'RV-{uuid.uuid4().hex[:10]}'
    review_repository.insert((
        review_id,
        contract['id'],
        state['trace_id'],
        state['risk_score'],
        state['risk_level'],
        1 if legal_required else 0,
        status,
        jdump(summary),
        audit_service.utcnow(),
    ))
    legal_review_id = checkpointer.save_pending(review_id, contract['id']) if legal_required else None
    return {'review_id': review_id, 'legal_review_id': legal_review_id, 'status': status, 'summary': summary}
