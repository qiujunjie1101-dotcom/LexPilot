"""线上 Bad Case 自动转换并沉淀为评测用例的工具。"""
from __future__ import annotations

from typing import Any

from contract_reviewer.infrastructure.repositories.bad_case_repository import bad_case_repository


def pending_bad_cases() -> list[dict[str, Any]]:
    return [item for item in bad_case_repository.list_all() if item['status'] == 'open']


def to_eval_case(
    bad_case: dict[str, Any],
    contract_id: str,
    expected_level: str,
    required_issue: str | None = None,
    expected_legal: bool = True,
) -> dict[str, Any]:
    return {
        'id': f"EVAL-{bad_case['id']}",
        'contract_id': contract_id,
        'expected_level': expected_level,
        'expected_legal': expected_legal,
        'required_issue': required_issue,
        'source_bad_case': bad_case['id'],
        'note': bad_case['note'],
    }


def convert_open_bad_cases(contract_id: str, expected_level: str, required_issue: str | None = None) -> list[dict[str, Any]]:
    return [
        to_eval_case(bad_case, contract_id, expected_level, required_issue)
        for bad_case in pending_bad_cases()
    ]
