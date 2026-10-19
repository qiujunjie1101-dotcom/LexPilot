"""条款结构化字段及标准化归一模型。"""
from __future__ import annotations

from typing import Literal, TypedDict


class NormalizedClause(TypedDict, total=False):
    payment_days: int
    payment_trigger: Literal['invoice_received', 'final_customer_acceptance']
    liability_cap: Literal['contract_amount', 'unlimited']
    background_ip_owner: Literal['original_owner', 'customer']
    source_code_delivery: bool
    auto_renewal: bool
    renewal_months: int
    notice_days: int
    unilateral_termination_customer_only: bool
    jurisdiction: Literal['provider_location', 'customer_location']
