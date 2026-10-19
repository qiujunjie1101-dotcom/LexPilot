"""审查结果仓储。"""
from __future__ import annotations

from typing import Any

from ..database import execute, row, rows


class ReviewRepository:
    def insert(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO review_results VALUES (?,?,?,?,?,?,?,?,?)', values)

    def recent(self, limit: int = 100) -> list[dict[str, Any]]:
        return rows('SELECT * FROM review_results ORDER BY created_at DESC LIMIT ?', (limit,))

    def get(self, review_id: str) -> dict[str, Any] | None:
        return row('SELECT * FROM review_results WHERE id=?', (review_id,))

    def update_status(self, review_id: str, status: str) -> None:
        execute('UPDATE review_results SET status=? WHERE id=?', (status, review_id))

    def count(self) -> int:
        return row('SELECT COUNT(*) AS c FROM review_results')['c']

    def risk_counts(self) -> dict[str, int]:
        return {item['risk_level']: item['c'] for item in rows('SELECT risk_level,COUNT(*) AS c FROM review_results GROUP BY risk_level')}


review_repository = ReviewRepository()
