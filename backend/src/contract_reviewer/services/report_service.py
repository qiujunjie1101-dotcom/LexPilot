"""审查审计报告、Diff 对照表与看板指标生成服务。"""
from __future__ import annotations

from typing import Any

from ..infrastructure.database import jload
from ..infrastructure.repositories.contract_repository import contract_repository
from ..infrastructure.repositories.legal_review_repository import legal_review_repository
from ..infrastructure.repositories.review_repository import review_repository


def build_summary(
    contract: dict[str, Any],
    diffs: list[dict[str, Any]],
    issues: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    reviewed_clause_types: list[str],
    changed_clause_types: list[str],
    risk_score: int,
    risk_level: str,
    legal_review_required: bool,
    recommendation: dict[str, Any],
) -> dict[str, Any]:
    return {
        'contract_id': contract['id'],
        'title': contract['title'],
        'contract_type': contract['contract_type'],
        'version': contract['version'],
        'parent_contract_id': contract.get('parent_contract_id'),
        'incremental_review': bool(contract.get('parent_contract_id')),
        'reviewed_clause_types': reviewed_clause_types,
        'changed_clause_types': changed_clause_types,
        'diffs': diffs,
        'issues': issues,
        'evidence': [
            {
                'id': item['id'],
                'title': item['title'],
                'version': item['version'],
                'clause_type': item['clause_type'],
                'content': item['content'],
                'rerank_score': item['rerank_score'],
            }
            for item in evidence
        ],
        'risk_score': risk_score,
        'risk_level': risk_level,
        'legal_review_required': legal_review_required,
        'summary': recommendation,
    }


def list_reviews() -> list[dict[str, Any]]:
    data = review_repository.recent()
    for item in data:
        item['summary'] = jload(item.pop('summary_json'), {})
    return data


def dashboard_stats(mock_mode: bool) -> dict[str, Any]:
    return {
        'contracts': contract_repository.count(),
        'reviews': review_repository.count(),
        'pending_legal_reviews': legal_review_repository.pending_count(),
        'risk_counts': review_repository.risk_counts(),
        'mock_mode': mock_mode,
    }
