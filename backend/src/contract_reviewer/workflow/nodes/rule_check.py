"""节点：确定性红线规则引擎判定。"""
from __future__ import annotations

from time import perf_counter
from typing import Any

from ...services import audit_service
from ...services.rule_engine import apply_rules, missing_clause_issues
from ..state import ReviewState


def run(state: ReviewState, clause: dict[str, Any]) -> list[dict[str, str]]:
    started = perf_counter()
    issues = apply_rules(clause)
    audit_service.trace(
        state['trace_id'],
        'rule_check',
        {'clause_type': clause['clause_type'], 'issues': issues},
        started,
    )
    return issues


def check_missing(state: ReviewState) -> list[dict[str, str]]:
    contract = state['contract']
    if contract.get('parent_contract_id'):
        return []
    return missing_clause_issues(contract, state['template'])
