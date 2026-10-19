"""线上坏例（Bad Case）仓储。"""
from __future__ import annotations

from typing import Any

from ..database import execute, rows


class BadCaseRepository:
    def list_all(self) -> list[dict[str, Any]]:
        return rows('SELECT * FROM bad_cases ORDER BY id')

    def insert(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO bad_cases VALUES (?,?,?,?,?)', values)


bad_case_repository = BadCaseRepository()
