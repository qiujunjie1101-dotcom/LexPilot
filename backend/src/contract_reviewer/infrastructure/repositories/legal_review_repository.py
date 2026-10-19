"""人工复核单仓储。"""
from __future__ import annotations

from typing import Any

from ..database import execute, row, rows


class LegalReviewRepository:
    def insert_pending(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO legal_reviews VALUES (?,?,?,?,?,?,?,?)', values)

    def get(self, legal_review_id: str) -> dict[str, Any] | None:
        return row('SELECT * FROM legal_reviews WHERE id=?', (legal_review_id,))

    def list_with_contracts(self) -> list[dict[str, Any]]:
        return rows(
            'SELECT lr.*,c.title,c.version,rr.risk_level,rr.risk_score FROM legal_reviews lr '
            'JOIN contracts c ON c.id=lr.contract_id JOIN review_results rr ON rr.id=lr.review_result_id '
            'ORDER BY lr.created_at DESC'
        )

    def update_decision(self, legal_review_id: str, status: str, comment: str, updated_at: str) -> None:
        execute(
            'UPDATE legal_reviews SET status=?,comment=?,updated_at=? WHERE id=?',
            (status, comment, updated_at, legal_review_id),
        )

    def pending_count(self) -> int:
        return row('SELECT COUNT(*) AS c FROM legal_reviews WHERE status="pending"')['c']


legal_review_repository = LegalReviewRepository()
