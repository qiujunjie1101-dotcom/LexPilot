from typing import Any, TypedDict
class ReviewState(TypedDict,total=False):
    contract_id:str; changed_clause_types:list[str]; diffs:list[dict[str,Any]]; issues:list[dict[str,Any]]; evidence:list[dict[str,Any]]; risk_score:int; risk_level:str; legal_review_required:bool

def langgraph_available()->bool:
    try: import langgraph; return True
    except Exception: return False

def architecture_note():
    return {'langgraph_available':langgraph_available(),'workflow_nodes':['parse_contract','classify_contract','incremental_diff','clause_diff','rule_check','legal_rag','risk_score','human_legal_review','finalize'],'note':'演示版将同一 State 节点逻辑直接执行，并将 HITL 状态持久化到 legal_reviews；安装 requirements 中 LangGraph 后可替换为 StateGraph 编排。'}
