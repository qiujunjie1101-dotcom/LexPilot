"""人工复核审批状态机流转与审计回写服务。"""
from __future__ import annotations

import uuid
from typing import Any

from ..common.constants import (
    LEGAL_REVIEW_STATUS_PENDING,
    REVIEW_STATUS_LEGAL_APPROVED,
    REVIEW_STATUS_LEGAL_REJECTED,
)
from ..common.exceptions import LegalReviewNotFoundError
from ..common.security import SecurityContext
from ..infrastructure.repositories.legal_review_repository import legal_review_repository
from ..infrastructure.repositories.review_repository import review_repository
from . import audit_service


class LegalReviewService:
    def create_pending(self, review_result_id: str, contract_id: str) -> str:
        legal_review_id = f'LR-{uuid.uuid4().hex[:10]}'
        legal_review_repository.insert_pending((
            legal_review_id,
            review_result_id,
            contract_id,
            'legal',
            LEGAL_REVIEW_STATUS_PENDING,
            '',
            audit_service.utcnow(),
            None,
        ))
        return legal_review_id

    def list_reviews(self) -> list[dict[str, Any]]:
        return legal_review_repository.list_with_contracts()

    def decide(self, legal_review_id: str, decision: str, comment: str, ctx: SecurityContext) -> dict[str, Any]:
        item = legal_review_repository.get(legal_review_id)
        if not item:
            raise LegalReviewNotFoundError(legal_review_id)
        if item['status'] != LEGAL_REVIEW_STATUS_PENDING:
            return dict(item)
        legal_review_repository.update_decision(legal_review_id, decision, comment, audit_service.utcnow())
        review_repository.update_status(
            item['review_result_id'],
            REVIEW_STATUS_LEGAL_APPROVED if decision == 'approved' else REVIEW_STATUS_LEGAL_REJECTED,
        )
        audit_service.audit(ctx, item['contract_id'], 'legal_review_decision', {
            'legal_review_id': legal_review_id,
            'decision': decision,
            'comment': comment,
        })
        return legal_review_repository.get(legal_review_id) or {}


legal_review_service = LegalReviewService()
