"""合同生命周期与版本关联业务服务。"""
from __future__ import annotations

import hashlib
import uuid
from typing import Any

from ..common.security import SecurityContext
from ..infrastructure.database import jdump
from ..infrastructure.repositories.contract_repository import contract_repository
from . import audit_service, clause_extractor, document_service


class ContractService:
    def load(self, contract_id: str) -> dict[str, Any]:
        return contract_repository.get_with_clauses(contract_id)

    def list_visible(self, ctx: SecurityContext) -> list[dict[str, Any]]:
        return contract_repository.list_visible(ctx)

    def import_contract(
        self,
        title: str,
        contract_type: str,
        content: str,
        amount: float | None,
        parent_contract_id: str | None,
        ctx: SecurityContext,
    ) -> dict[str, Any]:
        contract_id = f'CT-UP-{uuid.uuid4().hex[:8]}'
        version = 'V1'
        if parent_contract_id:
            parent = contract_repository.get_with_clauses(parent_contract_id)
            try:
                version = f"V{int(parent['version'].lstrip('V')) + 1}"
            except Exception:
                version = 'V2'

        contract_repository.insert((
            contract_id,
            title,
            contract_type,
            version,
            parent_contract_id,
            ctx.user_id,
            ctx.department_id,
            'active',
            amount,
            content,
            hashlib.sha256(content.encode()).hexdigest(),
            audit_service.utcnow(),
        ))

        parsed = [
            (clause_type, text, clause_extractor.normalize(clause_type, text))
            for clause_type, text in document_service.split_clauses(content)
        ]
        if not parsed:
            parsed = [('payment', content[:1200], {'payment_days': 30, 'payment_trigger': 'invoice_received'})]

        for index, (clause_type, text, normalized) in enumerate(parsed, 1):
            contract_repository.insert_clause((
                f'{contract_id}-{clause_type}-{index}',
                contract_id,
                clause_type,
                clause_type,
                text,
                jdump(normalized),
                index,
            ))
        audit_service.audit(ctx, contract_id, 'contract_import', {'title': title, 'parsed_clause_count': len(parsed)})
        return self.load(contract_id)


contract_service = ContractService()
