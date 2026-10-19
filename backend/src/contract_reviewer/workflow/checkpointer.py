"""状态检查点持久化：用 legal_reviews 承载人机协同断点与恢复。"""
from __future__ import annotations

from typing import Any

from ..infrastructure.repositories.legal_review_repository import legal_review_repository
from ..services.legal_review_service import legal_review_service


class LegalReviewCheckpointer:
    def save_pending(self, review_result_id: str, contract_id: str) -> str:
        return legal_review_service.create_pending(review_result_id, contract_id)

    def load(self, legal_review_id: str) -> dict[str, Any] | None:
        return legal_review_repository.get(legal_review_id)


checkpointer = LegalReviewCheckpointer()
