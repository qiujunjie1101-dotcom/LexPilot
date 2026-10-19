"""条款字段级比对与差异分析服务。"""
from __future__ import annotations

from typing import Any

from ..infrastructure.repositories.contract_repository import contract_repository


def diff_clause(clause: dict[str, Any], standard: dict[str, Any] | None) -> dict[str, Any]:
    actual = clause['normalized']
    expected = standard['normalized'] if standard else {}
    changes = []
    for key in sorted(set(actual) | set(expected)):
        if actual.get(key) != expected.get(key):
            changes.append(f'{key}: {expected.get(key)!r} -> {actual.get(key)!r}')
    return {'clause_type': clause['clause_type'], 'title': clause['title'], 'actual': actual, 'standard': expected, 'changes': changes}


def changed_clause_types(contract: dict[str, Any]) -> list[str]:
    if not contract.get('parent_contract_id'):
        return [clause['clause_type'] for clause in contract['clauses']]
    parent = contract_repository.get_with_clauses(contract['parent_contract_id'])
    old = {clause['clause_type']: clause['normalized'] for clause in parent['clauses']}
    new = {clause['clause_type']: clause['normalized'] for clause in contract['clauses']}
    return [key for key in sorted(set(old) | set(new)) if old.get(key) != new.get(key)]
