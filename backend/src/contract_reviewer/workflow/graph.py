"""审查工作流组装与执行入口。

按 StateGraph 拓扑顺序装配 nodes：document_parse → clause_extract →
incremental_diff → classify → (clause_diff → rule_check → legal_rag)* →
risk_score → recommendation → hitl_gate → finalize。

逐条款阶段保持顺序执行，以复现旧实现的 Trace 顺序与同步 HITL 行为；
节点签名与 ReviewState 契约同时兼容 LangGraph StateGraph 编排。
"""
from __future__ import annotations

from typing import Any

from ..common.logger import set_trace_id
from ..common.security import SecurityContext
from ..services import audit_service
from . import edges
from .nodes import (
    clause_diff,
    clause_extract,
    classify,
    document_parse,
    finalize,
    hitl_gate,
    incremental_diff,
    legal_rag,
    recommendation,
    risk_score,
    rule_check,
)
from .state import ReviewState


def run_review(contract_id: str, ctx: SecurityContext) -> dict[str, Any]:
    trace_id = audit_service.new_trace_id()
    set_trace_id(trace_id)
    state: ReviewState = ReviewState(contract_id=contract_id, trace_id=trace_id, context=ctx)

    state.update(document_parse.parse_document(state))
    state.update(clause_extract.extract_clauses(state))
    state.update(incremental_diff.analyze(state))
    state.update(classify.classify(state))

    diffs: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    reviewed: list[str] = []
    for clause in state['contract']['clauses']:
        if not edges.should_review_clause(state, clause):
            continue
        reviewed.append(clause['clause_type'])
        diffs.append(clause_diff.run(state, clause))
        issues.extend(rule_check.run(state, clause))
        evidence.extend(legal_rag.run(state, clause))

    issues.extend(rule_check.check_missing(state))
    evidence = list({item['id']: item for item in evidence}.values())
    state.update({
        'diffs': diffs,
        'issues': issues,
        'evidence': evidence,
        'reviewed_clause_types': reviewed,
    })

    state.update(risk_score.assess(state))
    state.update(recommendation.generate(state))
    state.update(hitl_gate.gate(state))
    state.update(finalize.finalize(state))
    return state['summary']


def langgraph_available() -> bool:
    try:
        import langgraph
        return True
    except Exception:
        return False


def architecture_note() -> dict[str, Any]:
    return {
        'langgraph_available': langgraph_available(),
        'workflow_nodes': [
            'parse_contract',
            'classify_contract',
            'incremental_diff',
            'clause_diff',
            'rule_check',
            'legal_rag',
            'risk_score',
            'human_legal_review',
            'finalize',
        ],
        'note': '演示版将同一 State 节点逻辑直接执行，并将 HITL 状态持久化到 legal_reviews；安装 requirements 中 LangGraph 后可替换为 StateGraph 编排。',
    }
