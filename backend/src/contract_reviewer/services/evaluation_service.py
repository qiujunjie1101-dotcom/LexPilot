"""评测基准用例定义与批量运行服务。"""
from __future__ import annotations

from typing import Any

from ..common.security import SecurityContext

CASES = [
    {'id': 'EVAL-001', 'contract_id': 'CT-SAAS-STD', 'expected_level': 'low', 'expected_legal': False, 'required_issue': None},
    {'id': 'EVAL-002', 'contract_id': 'CT-SALES-180', 'expected_level': 'high', 'expected_legal': True, 'required_issue': 'LEGAL-PAY-001'},
    {'id': 'EVAL-003', 'contract_id': 'CT-SAAS-CRITICAL', 'expected_level': 'critical', 'expected_legal': True, 'required_issue': 'LEGAL-LIAB-001'},
    {'id': 'EVAL-004', 'contract_id': 'CT-SAAS-RENEW', 'expected_level': 'high', 'expected_legal': True, 'required_issue': 'LEGAL-RENEW-001'},
    {'id': 'EVAL-005', 'contract_id': 'CT-SAAS-V2', 'expected_level': 'critical', 'expected_legal': True, 'required_issue': 'LEGAL-LIAB-001', 'expected_changed_only': ['liability']},
]


def run_eval() -> dict[str, Any]:
    from ..workflow.graph import run_review

    ctx = SecurityContext('sales-001', 'sales', 'sales-east', ('all', 'sales'))
    results = []
    for case in CASES:
        answer = run_review(case['contract_id'], ctx)
        issue_ids = {issue['rule_id'] for issue in answer['issues']}
        passed = answer['risk_level'] == case['expected_level'] and answer['legal_review_required'] == case['expected_legal']
        if case.get('required_issue'):
            passed = passed and case['required_issue'] in issue_ids
        if case.get('expected_changed_only'):
            passed = passed and answer['reviewed_clause_types'] == case['expected_changed_only']
        results.append({
            'id': case['id'],
            'contract_id': case['contract_id'],
            'passed': passed,
            'expected': case,
            'actual': {
                'risk_level': answer['risk_level'],
                'legal_review_required': answer['legal_review_required'],
                'reviewed_clause_types': answer['reviewed_clause_types'],
                'issue_ids': sorted(issue_ids),
            },
        })
    return {'passed': sum(1 for item in results if item['passed']), 'total': len(results), 'results': results}
