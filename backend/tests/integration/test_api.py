from __future__ import annotations

from fastapi.testclient import TestClient

from contract_reviewer.main import app

SALES = {'x-user-id': 'sales-001', 'x-role': 'sales', 'x-department-id': 'sales-east', 'x-groups': 'all,sales'}
LEGAL = {'x-user-id': 'legal-001', 'x-role': 'legal', 'x-department-id': 'legal', 'x-groups': 'all,legal'}


def test_health_and_runtime():
    with TestClient(app) as client:
        assert client.get('/health').json() == {'status': 'ok'}
        runtime = client.get('/api/runtime', headers=SALES).json()
        assert runtime['mock_mode'] is True
        assert runtime['langgraph_available'] is True
        assert 'finalize' in runtime['workflow_nodes']


def test_contract_list_detail_and_trace_flow():
    with TestClient(app) as client:
        contracts = client.get('/api/contracts', headers=SALES).json()
        assert any(item['id'] == 'CT-SAAS-CRITICAL' for item in contracts)

        detail = client.get('/api/contracts/CT-SAAS-CRITICAL', headers=SALES).json()
        assert len(detail['clauses']) == 6

        review = client.post('/api/contracts/CT-SAAS-CRITICAL/review', headers=SALES).json()
        assert review['risk_level'] == 'critical'
        assert review['legal_review_required'] is True

        traces = client.get(f"/api/traces/{review['trace_id']}", headers=SALES).json()
        nodes = [item['node'] for item in traces]
        assert nodes[0] == 'incremental_diff'
        assert nodes.count('clause_diff') == 6
        assert nodes.count('rule_check') == 6
        assert nodes.count('legal_rag') == 6
        assert nodes[-1] == 'recommendation'


def test_human_review_permission_and_decision():
    with TestClient(app) as client:
        review = client.post('/api/contracts/CT-SALES-180/review', headers=SALES).json()
        assert client.get('/api/legal-reviews', headers=SALES).status_code == 403

        legal_rows = client.get('/api/legal-reviews', headers=LEGAL).json()
        current = next(item for item in legal_rows if item['id'] == review['legal_review_id'])
        assert current['status'] == 'pending'

        decision = client.post(
            f"/api/legal-reviews/{review['legal_review_id']}/decision",
            json={'decision': 'approved', 'comment': '同意推进'},
            headers=LEGAL,
        ).json()
        assert decision['status'] == 'approved'


def test_import_contract_and_incremental_review():
    content = '[payment] 甲方在收到发票后45日内付款。\n[liability] 乙方承担无限责任。\n[ip] 乙方交付全部源代码。'
    with TestClient(app) as client:
        imported = client.post('/api/contracts/import', json={
            'title': '集成测试合同',
            'contract_type': 'saas',
            'content': content,
            'amount': 500000,
            'parent_contract_id': 'CT-SAAS-V1',
        }, headers=SALES).json()
        assert imported['version'] == 'V2'
        assert len(imported['clauses']) == 3
        liability = next(item for item in imported['clauses'] if item['clause_type'] == 'liability')
        assert liability['normalized']['liability_cap'] == 'unlimited'

        review = client.post(f"/api/contracts/{imported['id']}/review", headers=SALES).json()
        assert review['incremental_review'] is True
        assert review['risk_level'] == 'critical'


def test_knowledge_dashboard_bad_case_and_evaluation():
    with TestClient(app) as client:
        assert len(client.get('/api/templates', headers=SALES).json()) == 12
        playbooks = client.get('/api/playbooks', headers=SALES).json()
        assert {item['id'] for item in playbooks} >= {'PB-PAY', 'PB-LIAB', 'PB-JUR'}
        assert all(item['status'] == 'active' for item in playbooks)

        rules = client.get('/api/rules', headers=SALES).json()
        assert len(rules) == 9

        created = client.post('/api/bad-cases', json={
            'title': '回归坏例',
            'category': 'retrieval',
            'note': '旧版 Playbook 被召回',
        }, headers=SALES).json()
        assert created['status'] == 'open'
        assert any(item['id'] == created['id'] for item in client.get('/api/bad-cases', headers=SALES).json())

        dashboard = client.get('/api/dashboard', headers=SALES).json()
        assert dashboard['contracts'] >= 6
        assert 'risk_counts' in dashboard

        evaluation = client.post('/api/eval/run', headers=SALES).json()
        assert evaluation['passed'] == evaluation['total']
