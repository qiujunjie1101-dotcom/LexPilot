"""节点：文档内容读取与版式初解析。"""
from __future__ import annotations

from typing import Any

from ...services.contract_service import contract_service
from ..state import ReviewState


def parse_document(state: ReviewState) -> dict[str, Any]:
    return {'contract': contract_service.load(state['contract_id'])}
