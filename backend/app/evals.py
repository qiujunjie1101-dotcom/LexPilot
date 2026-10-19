from .security import SecurityContext
from .services import review_contract
CASES=[
 {'id':'EVAL-001','contract_id':'CT-SAAS-STD','expected_level':'low','expected_legal':False,'required_issue':None},
 {'id':'EVAL-002','contract_id':'CT-SALES-180','expected_level':'high','expected_legal':True,'required_issue':'LEGAL-PAY-001'},
 {'id':'EVAL-003','contract_id':'CT-SAAS-CRITICAL','expected_level':'critical','expected_legal':True,'required_issue':'LEGAL-LIAB-001'},
 {'id':'EVAL-004','contract_id':'CT-SAAS-RENEW','expected_level':'high','expected_legal':True,'required_issue':'LEGAL-RENEW-001'},
 {'id':'EVAL-005','contract_id':'CT-SAAS-V2','expected_level':'critical','expected_legal':True,'required_issue':'LEGAL-LIAB-001','expected_changed_only':['liability']},
]
def run_eval():
    ctx=SecurityContext('sales-001','sales','sales-east',('all','sales')); results=[]
    for case in CASES:
        a=review_contract(case['contract_id'],ctx); ids={x['rule_id'] for x in a['issues']}; passed=a['risk_level']==case['expected_level'] and a['legal_review_required']==case['expected_legal']
        if case.get('required_issue'): passed=passed and case['required_issue'] in ids
        if case.get('expected_changed_only'): passed=passed and a['reviewed_clause_types']==case['expected_changed_only']
        results.append({'id':case['id'],'contract_id':case['contract_id'],'passed':passed,'expected':case,'actual':{'risk_level':a['risk_level'],'legal_review_required':a['legal_review_required'],'reviewed_clause_types':a['reviewed_clause_types'],'issue_ids':sorted(ids)}})
    return {'passed':sum(1 for x in results if x['passed']),'total':len(results),'results':results}
