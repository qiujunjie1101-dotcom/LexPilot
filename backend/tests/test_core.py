from __future__ import annotations
import os
from pathlib import Path
os.environ['MOCK_MODE']='true'; os.environ['DATABASE_PATH']=str(Path(__file__).resolve().parent/'test_legal_agent.db')
from app.db import db_path,row
from app.seed import seed
from app.security import SecurityContext
from app.services import legal_decision,review_contract
CTX=SecurityContext('sales-001','sales','sales-east',('all','sales')); LEGAL=SecurityContext('legal-001','legal','legal',('all','legal'))
def setup_function():
    p=db_path()
    if p.exists(): p.unlink()
    seed(True)
def test_standard_contract_low_risk():
    r=review_contract('CT-SAAS-STD',CTX); assert r['risk_level']=='low'; assert r['legal_review_required'] is False; assert r['issues']==[]
def test_payment_180_high_risk_and_human_review():
    r=review_contract('CT-SALES-180',CTX); assert r['risk_level']=='high'; assert r['legal_review_required'] is True; assert 'LEGAL-PAY-001' in {x['rule_id'] for x in r['issues']}; assert r['legal_review_id']
def test_critical_contract_and_legal_decision():
    r=review_contract('CT-SAAS-CRITICAL',CTX); ids={x['rule_id'] for x in r['issues']}; assert r['risk_level']=='critical'; assert {'LEGAL-LIAB-001','LEGAL-IP-002'}.issubset(ids); lr=legal_decision(r['legal_review_id'],'approved','已按法务意见修改后可推进',LEGAL); assert lr['status']=='approved'; assert row('SELECT status FROM review_results WHERE id=?',(r['review_id'],))['status']=='legal_approved'
def test_incremental_review_only_changed_liability():
    r=review_contract('CT-SAAS-V2',CTX); assert r['incremental_review'] is True; assert r['changed_clause_types']==['liability']; assert r['reviewed_clause_types']==['liability']; assert r['risk_level']=='critical'
