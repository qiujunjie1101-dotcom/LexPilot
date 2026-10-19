"""确定性审查规则引擎：付款期、无限责任等红线检测。"""
from __future__ import annotations

from typing import Any

from ..common.constants import (
    RULE_AUTO_RENEWAL,
    RULE_BACKGROUND_IP,
    RULE_JURISDICTION,
    RULE_MISSING_PREFIX,
    RULE_PAYMENT_ABOVE_60,
    RULE_PAYMENT_ABOVE_90,
    RULE_PAYMENT_TRIGGER,
    RULE_SOURCE_CODE_DELIVERY,
    RULE_UNILATERAL_TERMINATION,
    RULE_UNLIMITED_LIABILITY,
)
from ..tools import date_calculator


def _issue(rule_id: str, clause_type: str, severity: str, reason: str, suggestion: str) -> dict[str, str]:
    return {'rule_id': rule_id, 'clause_type': clause_type, 'severity': severity, 'reason': reason, 'suggestion': suggestion}


def apply_rules(clause: dict[str, Any]) -> list[dict[str, str]]:
    clause_type = clause['clause_type']
    normalized = clause['normalized']
    issues: list[dict[str, str]] = []
    if clause_type == 'payment':
        days = date_calculator.as_days(normalized.get('payment_days'))
        if date_calculator.exceeds(days, 90):
            issues.append(_issue(RULE_PAYMENT_ABOVE_90, clause_type, 'high', f'付款周期为 {days} 天，超过公司90天红线。', '建议改为收到有效发票后60天内付款，并避免绑定最终客户验收。'))
        elif date_calculator.exceeds(days, 60):
            issues.append(_issue(RULE_PAYMENT_ABOVE_60, clause_type, 'medium', f'付款周期为 {days} 天，超过标准60天。', '建议回调至60天以内。'))
        if normalized.get('payment_trigger') == 'final_customer_acceptance':
            issues.append(_issue(RULE_PAYMENT_TRIGGER, clause_type, 'high', '付款条件绑定甲方最终客户验收，回款条件不可控。', '建议改为甲方自身验收或收到发票后付款。'))
    elif clause_type == 'liability' and normalized.get('liability_cap') == 'unlimited':
        issues.append(_issue(RULE_UNLIMITED_LIABILITY, clause_type, 'critical', '合同约定乙方承担无限责任。', '建议将累计责任上限限定为合同总金额，特殊责任由法务单独设计例外。'))
    elif clause_type == 'ip':
        if normalized.get('background_ip_owner') == 'customer':
            issues.append(_issue(RULE_BACKGROUND_IP, clause_type, 'critical', '背景知识产权被要求转让给客户。', '建议明确双方背景知识产权归原权利人所有，仅授予项目必要使用权。'))
        if normalized.get('source_code_delivery') is True:
            issues.append(_issue(RULE_SOURCE_CODE_DELIVERY, clause_type, 'critical', '合同要求交付全部源代码或底层算法。', '原则上删除源代码交付义务；确需交付时必须法务与技术负责人专项审批。'))
    elif clause_type == 'renewal' and normalized.get('auto_renewal') is True:
        months = int(normalized.get('renewal_months') or 0)
        severity = 'high' if months >= 36 else 'medium'
        issues.append(_issue(RULE_AUTO_RENEWAL, clause_type, severity, f'合同存在自动续约 {months} 个月条款。', '建议改为到期后双方书面确认续约；如保留自动续约，应缩短期限并设置明确通知窗口。'))
    elif clause_type == 'termination' and normalized.get('unilateral_termination_customer_only') is True:
        issues.append(_issue(RULE_UNILATERAL_TERMINATION, clause_type, 'high', '仅客户享有单方解除权，权利义务明显不对等。', '建议增加对等终止权及合理补偿机制。'))
    elif clause_type == 'jurisdiction' and normalized.get('jurisdiction') == 'customer_location':
        issues.append(_issue(RULE_JURISDICTION, clause_type, 'medium', '争议管辖仅约定客户所在地。', '建议改为我方所在地或双方可接受的中立管辖地。'))
    return issues


def missing_clause_issues(contract: dict[str, Any], template: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    actual = {clause['clause_type'] for clause in contract['clauses']}
    for clause_type, standard in template.items():
        if standard['required'] and clause_type not in actual:
            issues.append(_issue(
                f'{RULE_MISSING_PREFIX}{clause_type.upper()}',
                clause_type,
                standard['severity_if_missing'],
                f'缺少必备条款：{clause_type}',
                '补充公司标准条款后再推进。',
            ))
    return issues


RULE_CATALOG: list[dict[str, str]] = [
    {'rule_id': RULE_PAYMENT_ABOVE_90, 'clause_type': 'payment', 'severity': 'high', 'title': '付款周期超过90天红线'},
    {'rule_id': RULE_PAYMENT_ABOVE_60, 'clause_type': 'payment', 'severity': 'medium', 'title': '付款周期超过标准60天'},
    {'rule_id': RULE_PAYMENT_TRIGGER, 'clause_type': 'payment', 'severity': 'high', 'title': '付款条件绑定最终客户验收'},
    {'rule_id': RULE_UNLIMITED_LIABILITY, 'clause_type': 'liability', 'severity': 'critical', 'title': '乙方承担无限责任'},
    {'rule_id': RULE_BACKGROUND_IP, 'clause_type': 'ip', 'severity': 'critical', 'title': '背景知识产权转让给客户'},
    {'rule_id': RULE_SOURCE_CODE_DELIVERY, 'clause_type': 'ip', 'severity': 'critical', 'title': '要求交付源代码或底层算法'},
    {'rule_id': RULE_AUTO_RENEWAL, 'clause_type': 'renewal', 'severity': 'high', 'title': '自动续约期限过长'},
    {'rule_id': RULE_UNILATERAL_TERMINATION, 'clause_type': 'termination', 'severity': 'high', 'title': '仅客户享有单方解除权'},
    {'rule_id': RULE_JURISDICTION, 'clause_type': 'jurisdiction', 'severity': 'medium', 'title': '争议管辖约定在客户所在地'},
]


def enabled_rules() -> list[dict[str, str]]:
    return [dict(rule) for rule in RULE_CATALOG]
