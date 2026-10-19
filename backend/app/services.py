from __future__ import annotations
import hashlib, math, re, time, uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from .config import settings
from .db import execute, jdump, jload, row, rows
from .llm import chat_json
from .security import SecurityContext

RISK_WEIGHT={'low':5,'medium':20,'high':40,'critical':70}
def utcnow(): return datetime.now(timezone.utc).isoformat()
def trace(trace_id,node,detail,started): execute('INSERT INTO trace_events(trace_id,node,detail_json,latency_ms,created_at) VALUES (?,?,?,?,?)',(trace_id,node,jdump(detail),int((time.perf_counter()-started)*1000),utcnow()))
def audit(ctx,contract_id,action,detail,trace_id=None): execute('INSERT INTO audit_logs(trace_id,contract_id,actor_id,action,detail_json,created_at) VALUES (?,?,?,?,?,?)',(trace_id,contract_id,ctx.user_id,action,jdump(detail),utcnow()))

def tokenize(text:str)->list[str]:
    ascii_tokens=re.findall(r'[a-z0-9_\-]{2,}',text.lower()); chinese=''.join(re.findall(r'[\u4e00-\u9fff]',text)); return ascii_tokens+[chinese[i:i+2] for i in range(max(0,len(chinese)-1))]
def hash_vector(text:str,dims:int=96)->list[float]:
    vec=[0.0]*dims
    for token in tokenize(text): vec[int.from_bytes(hashlib.sha256(token.encode()).digest()[:2],'big')%dims]+=1
    norm=math.sqrt(sum(v*v for v in vec)) or 1; return [v/norm for v in vec]
def cosine(a,b): return sum(x*y for x,y in zip(a,b))
def lexical_score(query,text):
    q=tokenize(query); t=set(tokenize(text)); return 0 if not q else sum(1 for x in q if x in t)/len(q)

def legal_rag(contract_type,clause_type,query,ctx,top_k=3):
    candidates=rows('SELECT * FROM playbooks WHERE status="active" AND contract_type IN (?,"saas","sales") AND clause_type=?',(contract_type,clause_type)); allowed=[]
    for doc in candidates:
        acl={x.strip() for x in doc['acl_groups'].split(',') if x.strip()}
        if 'all' in acl or acl.intersection(ctx.groups) or ctx.role in acl: allowed.append(doc)
    qv=hash_vector(query); bm=sorted(allowed,key=lambda d:lexical_score(query,d['content']),reverse=True); vs=sorted(allowed,key=lambda d:cosine(qv,hash_vector(d['content'])),reverse=True)
    scores=defaultdict(float); docs={d['id']:d for d in allowed}
    for ranking in (bm,vs):
        for rank,d in enumerate(ranking,1): scores[d['id']]+=1/(60+rank)
    out=[]
    for did in sorted(scores,key=scores.get,reverse=True)[:top_k]:
        d=dict(docs[did]); d['rrf_score']=round(scores[did],6); d['rerank_score']=round(.65*lexical_score(query,d['content'])+.35*cosine(qv,hash_vector(d['content'])),4); out.append(d)
    return sorted(out,key=lambda x:x['rerank_score'],reverse=True)

def load_contract(contract_id):
    c=row('SELECT * FROM contracts WHERE id=?',(contract_id,));
    if not c: raise KeyError(contract_id)
    c['clauses']=[]
    for item in rows('SELECT * FROM clauses WHERE contract_id=? ORDER BY sort_order',(contract_id,)):
        item['normalized']=jload(item.pop('normalized_json'),{}); c['clauses'].append(item)
    return c

def load_template(contract_type):
    out={}
    for item in rows('SELECT * FROM standard_clauses WHERE contract_type=? AND status="active"',(contract_type,)):
        item['normalized']=jload(item.pop('normalized_json'),{}); out[item['clause_type']]=item
    return out

def changed_clause_types(contract):
    if not contract.get('parent_contract_id'): return [c['clause_type'] for c in contract['clauses']]
    parent=load_contract(contract['parent_contract_id']); old={c['clause_type']:c['normalized'] for c in parent['clauses']}; new={c['clause_type']:c['normalized'] for c in contract['clauses']}
    return [k for k in sorted(set(old)|set(new)) if old.get(k)!=new.get(k)]

def clause_diff(clause,standard):
    actual=clause['normalized']; expected=standard['normalized'] if standard else {}; changes=[]
    for key in sorted(set(actual)|set(expected)):
        if actual.get(key)!=expected.get(key): changes.append(f'{key}: {expected.get(key)!r} -> {actual.get(key)!r}')
    return {'clause_type':clause['clause_type'],'title':clause['title'],'actual':actual,'standard':expected,'changes':changes}
def _issue(rule_id,clause_type,severity,reason,suggestion): return {'rule_id':rule_id,'clause_type':clause_type,'severity':severity,'reason':reason,'suggestion':suggestion}
def apply_rules(clause):
    ctype=clause['clause_type']; n=clause['normalized']; issues=[]
    if ctype=='payment':
        days=int(n.get('payment_days') or 0)
        if days>90: issues.append(_issue('LEGAL-PAY-001',ctype,'high',f'付款周期为 {days} 天，超过公司90天红线。','建议改为收到有效发票后60天内付款，并避免绑定最终客户验收。'))
        elif days>60: issues.append(_issue('LEGAL-PAY-002',ctype,'medium',f'付款周期为 {days} 天，超过标准60天。','建议回调至60天以内。'))
        if n.get('payment_trigger')=='final_customer_acceptance': issues.append(_issue('LEGAL-PAY-003',ctype,'high','付款条件绑定甲方最终客户验收，回款条件不可控。','建议改为甲方自身验收或收到发票后付款。'))
    elif ctype=='liability' and n.get('liability_cap')=='unlimited': issues.append(_issue('LEGAL-LIAB-001',ctype,'critical','合同约定乙方承担无限责任。','建议将累计责任上限限定为合同总金额，特殊责任由法务单独设计例外。'))
    elif ctype=='ip':
        if n.get('background_ip_owner')=='customer': issues.append(_issue('LEGAL-IP-001',ctype,'critical','背景知识产权被要求转让给客户。','建议明确双方背景知识产权归原权利人所有，仅授予项目必要使用权。'))
        if n.get('source_code_delivery') is True: issues.append(_issue('LEGAL-IP-002',ctype,'critical','合同要求交付全部源代码或底层算法。','原则上删除源代码交付义务；确需交付时必须法务与技术负责人专项审批。'))
    elif ctype=='renewal' and n.get('auto_renewal') is True:
        months=int(n.get('renewal_months') or 0); sev='high' if months>=36 else 'medium'; issues.append(_issue('LEGAL-RENEW-001',ctype,sev,f'合同存在自动续约 {months} 个月条款。','建议改为到期后双方书面确认续约；如保留自动续约，应缩短期限并设置明确通知窗口。'))
    elif ctype=='termination' and n.get('unilateral_termination_customer_only') is True: issues.append(_issue('LEGAL-TERM-001',ctype,'high','仅客户享有单方解除权，权利义务明显不对等。','建议增加对等终止权及合理补偿机制。'))
    elif ctype=='jurisdiction' and n.get('jurisdiction')=='customer_location': issues.append(_issue('LEGAL-JUR-001',ctype,'medium','争议管辖仅约定客户所在地。','建议改为我方所在地或双方可接受的中立管辖地。'))
    return issues

def risk_level(score,issues):
    if any(i['severity']=='critical' for i in issues): return 'critical'
    if any(i['severity']=='high' for i in issues) or score>=51: return 'high'
    if any(i['severity']=='medium' for i in issues) or score>=21: return 'medium'
    return 'low'

def _recommendation_with_llm(contract,issues,evidence):
    fallback={'summary':f"{contract['title']} 共识别 {len(issues)} 个风险问题。" if issues else f"{contract['title']} 未发现明显红线。",'business_advice':'Critical/High 风险条款需法务确认后再对外回复；低风险合同可按标准流程推进。' if issues else '可进入常规业务审批，但仍应由业务负责人确认商业条件。','disclaimer':'该结果为企业内部合同初审辅助，不替代律师或法务的最终法律判断。'}
    if settings.mock_mode:return fallback
    system='你是企业法务合同审查 Copilot。只能依据提供的合同事实、规则命中和公司 Legal Playbook 生成内部初审摘要，不得声称提供最终法律意见。输出 JSON。'
    user=jdump({'contract':{'title':contract['title'],'type':contract['contract_type'],'version':contract['version']},'issues':issues,'evidence':[{'title':e['title'],'version':e['version'],'content':e['content']} for e in evidence],'required_json_keys':['summary','business_advice','disclaimer']})
    return chat_json(system,user,fallback)

def review_contract(contract_id,ctx):
    trace_id=f'trace-{uuid.uuid4().hex[:12]}'; contract=load_contract(contract_id)
    t=time.perf_counter(); changed=changed_clause_types(contract); trace(trace_id,'incremental_diff',{'parent_contract_id':contract.get('parent_contract_id'),'changed_clause_types':changed},t)
    template=load_template(contract['contract_type']); review_types=set(changed); diffs=[]; issues=[]; evidence=[]; reviewed=[]
    for clause in contract['clauses']:
        if clause['clause_type'] not in review_types: continue
        reviewed.append(clause['clause_type']); t=time.perf_counter(); diff=clause_diff(clause,template.get(clause['clause_type'])); diffs.append(diff); trace(trace_id,'clause_diff',diff,t)
        t=time.perf_counter(); ci=apply_rules(clause); issues.extend(ci); trace(trace_id,'rule_check',{'clause_type':clause['clause_type'],'issues':ci},t)
        t=time.perf_counter(); ev=legal_rag(contract['contract_type'],clause['clause_type'],f"{contract['contract_type']} {clause['clause_type']} {clause['content']}",ctx); evidence.extend(ev); trace(trace_id,'legal_rag',{'clause_type':clause['clause_type'],'evidence_ids':[e['id'] for e in ev]},t)
    if not contract.get('parent_contract_id'):
        actual={c['clause_type'] for c in contract['clauses']}
        for clause_type,std in template.items():
            if std['required'] and clause_type not in actual: issues.append(_issue(f'LEGAL-MISSING-{clause_type.upper()}',clause_type,std['severity_if_missing'],f'缺少必备条款：{clause_type}','补充公司标准条款后再推进。'))
    evidence=list({e['id']:e for e in evidence}.values()); score=min(100,sum(RISK_WEIGHT[i['severity']] for i in issues)); level=risk_level(score,issues); legal_required=level in {'high','critical'} or any(i['severity'] in {'high','critical'} for i in issues)
    t=time.perf_counter(); llm_summary=_recommendation_with_llm(contract,issues,evidence); trace(trace_id,'recommendation',llm_summary,t)
    summary={'contract_id':contract_id,'title':contract['title'],'contract_type':contract['contract_type'],'version':contract['version'],'parent_contract_id':contract.get('parent_contract_id'),'incremental_review':bool(contract.get('parent_contract_id')),'reviewed_clause_types':reviewed,'changed_clause_types':changed,'diffs':diffs,'issues':issues,'evidence':[{'id':e['id'],'title':e['title'],'version':e['version'],'clause_type':e['clause_type'],'content':e['content'],'rerank_score':e['rerank_score']} for e in evidence],'risk_score':score,'risk_level':level,'legal_review_required':legal_required,'summary':llm_summary}
    review_id=f'RV-{uuid.uuid4().hex[:10]}'; status='waiting_legal_review' if legal_required else 'precheck_passed'; execute('INSERT INTO review_results VALUES (?,?,?,?,?,?,?,?,?)',(review_id,contract_id,trace_id,score,level,1 if legal_required else 0,status,jdump(summary),utcnow()))
    legal_review_id=None
    if legal_required:
        legal_review_id=f'LR-{uuid.uuid4().hex[:10]}'; execute('INSERT INTO legal_reviews VALUES (?,?,?,?,?,?,?,?)',(legal_review_id,review_id,contract_id,'legal','pending','',utcnow(),None))
    audit(ctx,contract_id,'contract_review',{'review_id':review_id,'risk_level':level,'risk_score':score},trace_id); summary.update({'review_id':review_id,'trace_id':trace_id,'status':status,'legal_review_id':legal_review_id}); return summary

def legal_decision(review_id,decision,comment,ctx):
    item=row('SELECT * FROM legal_reviews WHERE id=?',(review_id,))
    if not item: raise KeyError(review_id)
    if item['status']!='pending': return dict(item)
    execute('UPDATE legal_reviews SET status=?,comment=?,updated_at=? WHERE id=?',(decision,comment,utcnow(),review_id)); execute('UPDATE review_results SET status=? WHERE id=?',('legal_approved' if decision=='approved' else 'legal_rejected',item['review_result_id'])); audit(ctx,item['contract_id'],'legal_review_decision',{'legal_review_id':review_id,'decision':decision,'comment':comment}); return row('SELECT * FROM legal_reviews WHERE id=?',(review_id,)) or {}

def import_contract(title,contract_type,content,amount,parent_contract_id,ctx):
    cid=f'CT-UP-{uuid.uuid4().hex[:8]}'; version='V1'
    if parent_contract_id:
        parent=load_contract(parent_contract_id)
        try: version=f"V{int(parent['version'].lstrip('V'))+1}"
        except Exception: version='V2'
    execute('INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(cid,title,contract_type,version,parent_contract_id,ctx.user_id,ctx.department_id,'active',amount,content,hashlib.sha256(content.encode()).hexdigest(),utcnow()))
    parsed=[]
    for line in [x.strip() for x in content.splitlines() if x.strip()]:
        m=re.match(r'^\[(payment|liability|ip|renewal|termination|jurisdiction)\]\s*(.*)$',line,re.I)
        if not m: continue
        ctype=m.group(1).lower(); text=m.group(2); norm={}
        if ctype=='payment':
            dm=re.search(r'(\d{1,3})\s*天',text); norm={'payment_days':int(dm.group(1)) if dm else 30,'payment_trigger':'final_customer_acceptance' if '最终客户' in text else 'invoice_received'}
        elif ctype=='liability': norm={'liability_cap':'unlimited' if '无限' in text else 'contract_amount'}
        elif ctype=='ip': norm={'background_ip_owner':'customer' if ('全部' in text and '归甲方' in text) else 'original_owner','source_code_delivery':'源代码' in text}
        elif ctype=='renewal':
            mm=re.search(r'(\d{1,3})\s*个月',text); norm={'auto_renewal':'自动续约' in text,'renewal_months':int(mm.group(1)) if mm else 0}
        elif ctype=='termination': norm={'unilateral_termination_customer_only':'甲方有权单方' in text}
        elif ctype=='jurisdiction': norm={'jurisdiction':'customer_location' if '甲方所在地' in text else 'provider_location'}
        parsed.append((ctype,text,norm))
    if not parsed: parsed=[('payment',content[:1200],{'payment_days':30,'payment_trigger':'invoice_received'})]
    for idx,(ctype,text,norm) in enumerate(parsed,1): execute('INSERT INTO clauses VALUES (?,?,?,?,?,?,?)',(f'{cid}-{ctype}-{idx}',cid,ctype,ctype,text,jdump(norm),idx))
    audit(ctx,cid,'contract_import',{'title':title,'parsed_clause_count':len(parsed)}); return load_contract(cid)
