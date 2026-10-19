from __future__ import annotations

from contract_reviewer.common.security import SecurityContext
from contract_reviewer.infrastructure.database import row
from contract_reviewer.services.legal_review_service import legal_review_service
from contract_reviewer.workflow.graph import run_review

CTX = SecurityContext('sales-001', 'sales', 'sales-east', ('all', 'sales'))
LEGAL = SecurityContext('legal-001', 'legal', 'legal', ('all', 'legal'))


def test_standard_contract_low_risk():
    result = run_review('CT-SAAS-STD', CTX)
    assert result['risk_level'] == 'low'
    assert result['legal_review_required'] is False
    assert result['issues'] == []


def test_payment_180_high_risk_and_human_review():
    result = run_review('CT-SALES-180', CTX)
    assert result['risk_level'] == 'high'
    assert result['legal_review_required'] is True
    assert 'LEGAL-PAY-001' in {issue['rule_id'] for issue in result['issues']}
    assert result['legal_review_id']


def test_critical_contract_and_legal_decision():
    result = run_review('CT-SAAS-CRITICAL', CTX)
    issue_ids = {issue['rule_id'] for issue in result['issues']}
    assert result['risk_level'] == 'critical'
    assert {'LEGAL-LIAB-001', 'LEGAL-IP-002'}.issubset(issue_ids)
    decision = legal_review_service.decide(result['legal_review_id'], 'approved', '已按法务意见修改后可推进', LEGAL)
    assert decision['status'] == 'approved'
    assert row('SELECT status FROM review_results WHERE id=?', (result['review_id'],))['status'] == 'legal_approved'


def test_incremental_review_only_changed_liability():
    result = run_review('CT-SAAS-V2', CTX)
    assert result['incremental_review'] is True
    assert result['changed_clause_types'] == ['liability']
    assert result['reviewed_clause_types'] == ['liability']
    assert result['risk_level'] == 'critical'
