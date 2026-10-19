"""合同与条款仓储。"""
from __future__ import annotations

from typing import Any

from ...common.constants import LEGAL_ROLES
from ...common.exceptions import ContractNotFoundError
from ...common.security import SecurityContext
from ..database import execute, jload, row, rows

_LIST_COLUMNS = 'id,title,contract_type,version,parent_contract_id,owner_user_id,department_id,status,amount,created_at'


class ContractRepository:
    def get(self, contract_id: str) -> dict[str, Any] | None:
        return row('SELECT * FROM contracts WHERE id=?', (contract_id,))

    def get_with_clauses(self, contract_id: str) -> dict[str, Any]:
        contract = self.get(contract_id)
        if not contract:
            raise ContractNotFoundError(contract_id)
        contract['clauses'] = []
        for item in rows('SELECT * FROM clauses WHERE contract_id=? ORDER BY sort_order', (contract_id,)):
            item['normalized'] = jload(item.pop('normalized_json'), {})
            contract['clauses'].append(item)
        return contract

    def list_visible(self, ctx: SecurityContext) -> list[dict[str, Any]]:
        if ctx.role in LEGAL_ROLES:
            return rows(f'SELECT {_LIST_COLUMNS} FROM contracts ORDER BY id')
        return rows(
            f'SELECT {_LIST_COLUMNS} FROM contracts WHERE owner_user_id=? OR department_id=? ORDER BY id',
            (ctx.user_id, ctx.department_id),
        )

    def insert(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', values)

    def insert_clause(self, values: tuple[Any, ...]) -> None:
        execute('INSERT INTO clauses VALUES (?,?,?,?,?,?,?)', values)

    def count(self) -> int:
        return row('SELECT COUNT(*) AS c FROM contracts')['c']

    def has_any(self) -> bool:
        return row('SELECT id FROM contracts LIMIT 1') is not None


contract_repository = ContractRepository()
