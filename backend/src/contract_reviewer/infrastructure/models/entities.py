"""数据库 ORM 实体模型定义（以 TypedDict 描述表结构，与 database.SCHEMA 一一对应）。"""
from __future__ import annotations

from typing import TypedDict


class ContractRow(TypedDict, total=False):
    id: str
    title: str
    contract_type: str
    version: str
    parent_contract_id: str | None
    owner_user_id: str
    department_id: str
    status: str
    amount: float | None
    content: str
    content_hash: str
    created_at: str


class ClauseRow(TypedDict, total=False):
    id: str
    contract_id: str
    clause_type: str
    title: str
    content: str
    normalized_json: str
    sort_order: int
    normalized: dict[str, object]


class StandardClauseRow(TypedDict, total=False):
    id: str
    contract_type: str
    clause_type: str
    standard_text: str
    normalized_json: str
    version: str
    status: str
    required: int
    severity_if_missing: str


class PlaybookRow(TypedDict, total=False):
    id: str
    title: str
    contract_type: str
    clause_type: str
    content: str
    version: str
    status: str
    acl_groups: str


class ReviewResultRow(TypedDict, total=False):
    id: str
    contract_id: str
    trace_id: str
    risk_score: int
    risk_level: str
    legal_review_required: int
    status: str
    summary_json: str
    created_at: str


class LegalReviewRow(TypedDict, total=False):
    id: str
    review_result_id: str
    contract_id: str
    reviewer_role: str
    status: str
    comment: str | None
    created_at: str
    updated_at: str | None


class TraceEventRow(TypedDict, total=False):
    id: int
    trace_id: str
    node: str
    detail_json: str
    latency_ms: int
    created_at: str


class AuditLogRow(TypedDict, total=False):
    id: int
    trace_id: str | None
    contract_id: str | None
    actor_id: str
    action: str
    detail_json: str
    created_at: str


class BadCaseRow(TypedDict, total=False):
    id: str
    title: str
    category: str
    status: str
    note: str
