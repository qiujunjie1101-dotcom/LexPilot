"""合同实体与版本信息数据模型。"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Clause(BaseModel):
    id: str
    contract_id: str
    clause_type: str
    title: str
    content: str
    normalized: dict[str, Any]
    sort_order: int


class Contract(BaseModel):
    id: str
    title: str
    contract_type: str
    version: str
    parent_contract_id: str | None = None
    owner_user_id: str
    department_id: str
    status: str
    amount: float | None = None
    created_at: str


class ContractDetail(Contract):
    content: str
    content_hash: str
    clauses: list[Clause]
