"""违约金利率年化计算与 LPR 4 倍上限合规校验工具。"""
from __future__ import annotations


def annualized_rate(principal: float, interest: float, days: int, days_per_year: int = 365) -> float:
    if principal <= 0 or days <= 0:
        raise ValueError('principal and days must be positive')
    return interest / principal * days_per_year / days


def lpr_cap(lpr: float, multiple: float = 4.0) -> float:
    """LPR 以小数传入（3.45% → 0.0345），返回司法保护上限利率。"""
    return lpr * multiple


def exceeds_lpr_cap(rate: float, lpr: float, multiple: float = 4.0) -> bool:
    return rate > lpr_cap(lpr, multiple)
