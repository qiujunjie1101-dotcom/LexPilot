"""节点：合同类型识别与审查基线确定。"""
from __future__ import annotations

from typing import Any

from ...services.knowledge_service import knowledge_service
from ..state import ReviewState


def classify(state: ReviewState) -> dict[str, Any]:
    contract = state['contract']
    return {'template': knowledge_service.load_template(contract['contract_type'])}
