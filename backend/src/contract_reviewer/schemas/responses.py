"""API 接口统一结构化响应包装 Schema。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class RuntimeInfo(BaseModel):
    mock_mode: bool
    deepseek_base_url: str
    deepseek_model: str
    langgraph_available: bool
    workflow_nodes: list[str]
    note: str


class DashboardStats(BaseModel):
    contracts: int
    reviews: int
    pending_legal_reviews: int
    risk_counts: dict[str, int]
    mock_mode: bool


class TraceEvent(BaseModel):
    id: int
    trace_id: str
    node: str
    detail: dict[str, Any]
    latency_ms: int
    created_at: str


class ReviewRecord(BaseModel):
    id: str
    contract_id: str
    trace_id: str
    risk_score: int
    risk_level: str
    legal_review_required: int
    status: str
    summary: dict[str, Any]
    created_at: str
