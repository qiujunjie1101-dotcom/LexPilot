from __future__ import annotations

from tests.harness.evaluators.metrics import level_accuracy, pass_rate, summarize
from tests.harness.bad_case_converter import to_eval_case


def test_pass_rate_and_level_accuracy():
    results = [
        {'passed': True, 'actual': {'risk_level': 'high'}, 'expected': {'expected_level': 'high'}},
        {'passed': False, 'actual': {'risk_level': 'low'}, 'expected': {'expected_level': 'critical'}},
    ]
    assert pass_rate(results) == 0.5
    assert level_accuracy(results) == 0.5
    report = {'passed': 1, 'total': 2, 'results': results}
    assert summarize(report) == {'passed': 1, 'total': 2, 'pass_rate': 0.5, 'level_accuracy': 0.5}


def test_bad_case_conversion_keeps_traceability():
    case = to_eval_case(
        {'id': 'BC-001', 'note': '旧版 Playbook 被误召回'},
        contract_id='CT-SAAS-V2',
        expected_level='critical',
        required_issue='LEGAL-LIAB-001',
    )
    assert case['id'] == 'EVAL-BC-001'
    assert case['source_bad_case'] == 'BC-001'
    assert case['expected_legal'] is True
