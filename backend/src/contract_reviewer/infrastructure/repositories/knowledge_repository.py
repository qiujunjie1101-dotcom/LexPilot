"""标准条款模板与 Legal Playbook 仓储。"""
from __future__ import annotations

from typing import Any

from ..database import rows


class KnowledgeRepository:
    def active_standard_clauses(self) -> list[dict[str, Any]]:
        return rows(
            'SELECT id,contract_type,clause_type,standard_text,version,status,required,severity_if_missing '
            'FROM standard_clauses WHERE status="active" ORDER BY contract_type,clause_type'
        )

    def standard_clauses_for(self, contract_type: str) -> list[dict[str, Any]]:
        return rows('SELECT * FROM standard_clauses WHERE contract_type=? AND status="active"', (contract_type,))

    def active_playbooks(self) -> list[dict[str, Any]]:
        return rows('SELECT * FROM playbooks WHERE status="active" ORDER BY contract_type,clause_type')

    def playbook_candidates(self, contract_type: str, clause_type: str) -> list[dict[str, Any]]:
        return rows(
            'SELECT * FROM playbooks WHERE status="active" AND contract_type IN (?,"saas","sales") AND clause_type=?',
            (contract_type, clause_type),
        )


knowledge_repository = KnowledgeRepository()
