"""风险量化评分、权重计算与等级映射服务。"""
from __future__ import annotations

from typing import Any

from ..common.constants import RISK_WEIGHT


def score(issues: list[dict[str, Any]]) -> int:
    return min(100, sum(RISK_WEIGHT[issue['severity']] for issue in issues))


def level(score_value: int, issues: list[dict[str, Any]]) -> str:
    if any(issue['severity'] == 'critical' for issue in issues):
        return 'critical'
    if any(issue['severity'] == 'high' for issue in issues) or score_value >= 51:
        return 'high'
    if any(issue['severity'] == 'medium' for issue in issues) or score_value >= 21:
        return 'medium'
    return 'low'


def legal_review_required(level_value: str, issues: list[dict[str, Any]]) -> bool:
    return level_value in {'high', 'critical'} or any(issue['severity'] in {'high', 'critical'} for issue in issues)
