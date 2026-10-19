from __future__ import annotations

import pytest

from contract_reviewer.services.rule_engine import apply_rules, enabled_rules, missing_clause_issues
from contract_reviewer.services.risk_service import legal_review_required, level, score


def clause(clause_type: str, **normalized):
    return {'clause_type': clause_type, 'title': clause_type, 'content': '', 'normalized': normalized}


def test_payment_over_90_and_final_acceptance_trigger():
    issues = apply_rules(clause('payment', payment_days=180, payment_trigger='final_customer_acceptance'))
    assert {issue['rule_id'] for issue in issues} == {'LEGAL-PAY-001', 'LEGAL-PAY-003'}
    assert {issue['severity'] for issue in issues} == {'high'}


def test_payment_between_60_and_90_is_medium():
    issues = apply_rules(clause('payment', payment_days=75, payment_trigger='invoice_received'))
    assert [issue['rule_id'] for issue in issues] == ['LEGAL-PAY-002']
    assert issues[0]['severity'] == 'medium'


def test_unlimited_liability_is_critical():
    issues = apply_rules(clause('liability', liability_cap='unlimited'))
    assert issues[0]['rule_id'] == 'LEGAL-LIAB-001'
    assert issues[0]['severity'] == 'critical'


def test_ip_transfer_and_source_code_delivery():
    issues = apply_rules(clause('ip', background_ip_owner='customer', source_code_delivery=True))
    assert [issue['rule_id'] for issue in issues] == ['LEGAL-IP-001', 'LEGAL-IP-002']


def test_auto_renewal_36_months_is_high():
    issues = apply_rules(clause('renewal', auto_renewal=True, renewal_months=36))
    assert issues[0]['rule_id'] == 'LEGAL-RENEW-001'
    assert issues[0]['severity'] == 'high'


def test_termination_and_jurisdiction_rules():
    assert apply_rules(clause('termination', unilateral_termination_customer_only=True))[0]['rule_id'] == 'LEGAL-TERM-001'
    assert apply_rules(clause('jurisdiction', jurisdiction='customer_location'))[0]['rule_id'] == 'LEGAL-JUR-001'


def test_missing_clause_issues_follow_template_severity():
    template = {
        'liability': {'required': 1, 'severity_if_missing': 'high', 'normalized': {}},
        'payment': {'required': 1, 'severity_if_missing': 'medium', 'normalized': {}},
        'ip': {'required': 0, 'severity_if_missing': 'high', 'normalized': {}},
    }
    issues = missing_clause_issues({'parent_contract_id': None, 'clauses': []}, template)
    assert [issue['rule_id'] for issue in issues] == ['LEGAL-MISSING-LIABILITY', 'LEGAL-MISSING-PAYMENT']
    assert [issue['severity'] for issue in issues] == ['high', 'medium']


def test_risk_score_is_weighted_and_capped():
    issues = [{'severity': 'critical'}, {'severity': 'high'}]
    assert score(issues) == 100
    assert level(score(issues), issues) == 'critical'
    assert legal_review_required('critical', issues) is True


def test_enabled_rules_catalog_is_read_only_copy():
    rules = enabled_rules()
    assert len(rules) == 9
    rules[0]['severity'] = 'tampered'
    assert enabled_rules()[0]['severity'] == 'high'


@pytest.mark.parametrize('severity,expected', [('medium', 'medium'), ('low', 'low')])
def test_level_mapping(severity, expected):
    assert level(0, [{'severity': severity}]) == expected
