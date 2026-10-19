"""风险定级准确度、用例通过率等评测指标。"""
from __future__ import annotations

from typing import Any


def pass_rate(results: list[dict[str, Any]]) -> float:
    if not results:
        return 0.0
    return sum(1 for item in results if item.get('passed')) / len(results)


def level_accuracy(results: list[dict[str, Any]]) -> float:
    graded = [item for item in results if item.get('expected', {}).get('expected_level')]
    if not graded:
        return 0.0
    hits = sum(
        1
        for item in graded
        if item['actual']['risk_level'] == item['expected']['expected_level']
    )
    return hits / len(graded)


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    results = report.get('results', [])
    return {
        'passed': report.get('passed', 0),
        'total': report.get('total', len(results)),
        'pass_rate': round(pass_rate(results), 4),
        'level_accuracy': round(level_accuracy(results), 4),
    }
