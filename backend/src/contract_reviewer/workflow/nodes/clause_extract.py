"""节点：条款结构化字段装载与归一校验。

导入阶段已由 clause_extractor 完成抽取，本节点只负责保证进入审查的条款
都带有 normalized 字段，避免脏数据影响后续比对。
"""
from __future__ import annotations

from typing import Any

from ..state import ReviewState


def extract_clauses(state: ReviewState) -> dict[str, Any]:
    contract = state['contract']
    for clause in contract['clauses']:
        normalized = clause.get('normalized')
        clause['normalized'] = normalized if isinstance(normalized, dict) else {}
    return {'contract': contract}
