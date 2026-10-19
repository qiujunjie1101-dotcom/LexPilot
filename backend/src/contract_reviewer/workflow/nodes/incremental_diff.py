"""节点：多版本父子合同增量变更识别。"""
from __future__ import annotations

from time import perf_counter
from typing import Any

from ...services import audit_service
from ...services.clause_diff_service import changed_clause_types
from ..state import ReviewState


def analyze(state: ReviewState) -> dict[str, Any]:
    contract = state['contract']
    started = perf_counter()
    changed = changed_clause_types(contract)
    audit_service.trace(
        state['trace_id'],
        'incremental_diff',
        {'parent_contract_id': contract.get('parent_contract_id'), 'changed_clause_types': changed},
        started,
    )
    return {'changed_clause_types': changed}
