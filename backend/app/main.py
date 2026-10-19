from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import init_db, jload, row, rows
from .evals import CASES, run_eval
from .graph import architecture_note
from .schemas import BadCaseRequest, ContractImportRequest, LegalDecisionRequest
from .security import SecurityContext, ensure_contract_access, ensure_legal_reviewer, get_security_context
from .seed import seed
from .services import import_contract, legal_decision, load_contract, review_contract

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    if not row('SELECT id FROM contracts LIMIT 1'): seed(True)
    yield

app=FastAPI(title='Enterprise Legal Contract Review Agent',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=list(settings.cors_origins),allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

@app.get('/health')
def health(): return {'status':'ok'}
@app.get('/api/runtime')
def runtime(): return {'mock_mode':settings.mock_mode,'deepseek_base_url':settings.deepseek_base_url,'deepseek_model':settings.deepseek_model,**architecture_note()}
@app.post('/api/admin/seed')
def reseed(ctx:SecurityContext=Depends(get_security_context)):
    if ctx.role not in {'legal','legal_admin'}: raise HTTPException(403,'LEGAL_ADMIN_REQUIRED')
    seed(True); return {'status':'seeded'}
@app.get('/api/dashboard')
def dashboard(ctx:SecurityContext=Depends(get_security_context)):
    return {'contracts':row('SELECT COUNT(*) AS c FROM contracts')['c'],'reviews':row('SELECT COUNT(*) AS c FROM review_results')['c'],'pending_legal_reviews':row('SELECT COUNT(*) AS c FROM legal_reviews WHERE status="pending"')['c'],'risk_counts':{x['risk_level']:x['c'] for x in rows('SELECT risk_level,COUNT(*) AS c FROM review_results GROUP BY risk_level')},'mock_mode':settings.mock_mode}
@app.get('/api/contracts')
def list_contracts(ctx:SecurityContext=Depends(get_security_context)):
    if ctx.role in {'legal','legal_admin'}: return rows('SELECT id,title,contract_type,version,parent_contract_id,owner_user_id,department_id,status,amount,created_at FROM contracts ORDER BY id')
    return rows('SELECT id,title,contract_type,version,parent_contract_id,owner_user_id,department_id,status,amount,created_at FROM contracts WHERE owner_user_id=? OR department_id=? ORDER BY id',(ctx.user_id,ctx.department_id))
@app.get('/api/contracts/{contract_id}')
def contract_detail(contract_id:str,ctx:SecurityContext=Depends(get_security_context)): ensure_contract_access(contract_id,ctx); return load_contract(contract_id)
@app.post('/api/contracts/import')
def contract_import(req:ContractImportRequest,ctx:SecurityContext=Depends(get_security_context)): return import_contract(req.title,req.contract_type,req.content,req.amount,req.parent_contract_id,ctx)
@app.post('/api/contracts/{contract_id}/review')
def contract_review(contract_id:str,ctx:SecurityContext=Depends(get_security_context)): ensure_contract_access(contract_id,ctx); return review_contract(contract_id,ctx)
@app.get('/api/reviews')
def review_list(ctx:SecurityContext=Depends(get_security_context)):
    data=rows('SELECT * FROM review_results ORDER BY created_at DESC LIMIT 100')
    for x in data: x['summary']=jload(x.pop('summary_json'),{})
    return data
@app.get('/api/legal-reviews')
def legal_reviews(ctx:SecurityContext=Depends(get_security_context)):
    ensure_legal_reviewer(ctx); return rows('SELECT lr.*,c.title,c.version,rr.risk_level,rr.risk_score FROM legal_reviews lr JOIN contracts c ON c.id=lr.contract_id JOIN review_results rr ON rr.id=lr.review_result_id ORDER BY lr.created_at DESC')
@app.post('/api/legal-reviews/{legal_review_id}/decision')
def legal_review_decision(legal_review_id:str,req:LegalDecisionRequest,ctx:SecurityContext=Depends(get_security_context)):
    ensure_legal_reviewer(ctx)
    try:return legal_decision(legal_review_id,req.decision,req.comment,ctx)
    except KeyError: raise HTTPException(404,'LEGAL_REVIEW_NOT_FOUND')
@app.get('/api/templates')
def templates(ctx:SecurityContext=Depends(get_security_context)): return rows('SELECT id,contract_type,clause_type,standard_text,version,status,required,severity_if_missing FROM standard_clauses WHERE status="active" ORDER BY contract_type,clause_type')
@app.get('/api/playbooks')
def playbooks(ctx:SecurityContext=Depends(get_security_context)):
    visible=[]
    for d in rows('SELECT * FROM playbooks WHERE status="active" ORDER BY contract_type,clause_type'):
        acl={x.strip() for x in d['acl_groups'].split(',') if x.strip()}
        if 'all' in acl or acl.intersection(ctx.groups) or ctx.role in acl: visible.append(d)
    return visible
@app.get('/api/traces/{trace_id}')
def traces(trace_id:str,ctx:SecurityContext=Depends(get_security_context)):
    data=rows('SELECT id,trace_id,node,detail_json,latency_ms,created_at FROM trace_events WHERE trace_id=? ORDER BY id',(trace_id,))
    for x in data: x['detail']=jload(x.pop('detail_json'),{})
    return data
@app.get('/api/bad-cases')
def bad_cases(ctx:SecurityContext=Depends(get_security_context)): return rows('SELECT * FROM bad_cases ORDER BY id')
@app.post('/api/bad-cases')
def add_bad_case(req:BadCaseRequest,ctx:SecurityContext=Depends(get_security_context)):
    import uuid
    from .db import execute
    bid=f'BC-{uuid.uuid4().hex[:8]}'; execute('INSERT INTO bad_cases VALUES (?,?,?,?,?)',(bid,req.title,req.category,'open',req.note)); return {'id':bid,**req.model_dump(),'status':'open'}
@app.get('/api/eval/cases')
def eval_cases(ctx:SecurityContext=Depends(get_security_context)): return CASES
@app.post('/api/eval/run')
def eval_run(ctx:SecurityContext=Depends(get_security_context)): return run_eval()
