"""LangGraph 全局流转状态契约。"""
from __future__ import annotations

from typing import Any, TypedDict

from ..common.security import SecurityContext


class ReviewState(TypedDict, total=False):
    contract_id: str
    trace_id: str
    context: SecurityContext
    contract: dict[str, Any]
    template: dict[str, dict[str, Any]]
    changed_clause_types: list[str]
    reviewed_clause_types: list[str]
    diffs: list[dict[str, Any]]
    issues: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    risk_score: int
    risk_level: str
    legal_review_required: bool
    legal_review_id: str | None
    review_id: str
    status: str
    recommendation: dict[str, Any]
    summary: dict[str, Any]
