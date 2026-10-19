"""节点：法务知识库与 Playbook 混合检索及重排。"""
from __future__ import annotations

from time import perf_counter
from typing import Any

from ...services import audit_service, rag_service
from ..state import ReviewState


def run(state: ReviewState, clause: dict[str, Any]) -> list[dict[str, Any]]:
    contract = state['contract']
    started = perf_counter()
    evidence = rag_service.search(
        contract['contract_type'],
        clause['clause_type'],
        f"{contract['contract_type']} {clause['clause_type']} {clause['content']}",
        state['context'],
    )
    audit_service.trace(
        state['trace_id'],
        'legal_rag',
        {'clause_type': clause['clause_type'], 'evidence_ids': [item['id'] for item in evidence]},
        started,
    )
    return evidence
