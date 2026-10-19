"""演示种子数据初始化服务。"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from ..infrastructure.database import connect, init_db, jdump

STANDARD = {
    'payment': ({'payment_days': 30, 'payment_trigger': 'invoice_received'}, '甲方在收到合法有效发票后30日内完成付款。'),
    'liability': ({'liability_cap': 'contract_amount'}, '除故意或重大过失外，双方累计责任上限不超过本合同总金额。'),
    'ip': ({'background_ip_owner': 'original_owner', 'source_code_delivery': False}, '双方各自保留背景知识产权；项目交付不当然转让源代码和底层算法。'),
    'renewal': ({'auto_renewal': False, 'renewal_months': 0}, '合同到期后如需续签，由双方另行书面确认。'),
    'termination': ({'unilateral_termination_customer_only': False}, '双方在约定条件下均享有合理终止权。'),
    'jurisdiction': ({'jurisdiction': 'provider_location'}, '争议由服务提供方所在地有管辖权的人民法院处理。'),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _contract(cid, title, ctype, version, content, amount, parent=None):
    return (cid, title, ctype, version, parent, 'sales-001', 'sales-east', 'active', amount, content, hash_text(content), now())


def seed(reset: bool = True) -> None:
    init_db()
    with connect() as conn:
        if reset:
            for table in ['legal_reviews', 'review_results', 'trace_events', 'audit_logs', 'bad_cases', 'clauses', 'contracts', 'playbooks', 'standard_clauses']:
                conn.execute(f'DELETE FROM {table}')
        for ctype in ['saas', 'sales']:
            for clause_type, (norm, text) in STANDARD.items():
                conn.execute(
                    'INSERT INTO standard_clauses VALUES (?,?,?,?,?,?,?,?,?)',
                    (f'STD-{ctype}-{clause_type}', ctype, clause_type, text, jdump(norm), '2026-V3', 'active', 1, 'high' if clause_type in {'liability', 'ip'} else 'medium'),
                )
        playbooks = [
            ('PB-PAY', '付款条款审查 Playbook', 'sales', 'payment', '公司销售合同付款周期原则上不超过60天；61-90天需业务负责人确认；超过90天原则上升级法务，并建议改回60天以内。', '2026-V3', 'active', 'all,legal,sales'),
            ('PB-LIAB', '责任限制 Playbook', 'saas', 'liability', '原则上不得接受无限责任。建议累计责任上限不超过合同总金额；如涉及故意、重大过失、保密或数据事件，由法务另行设计例外。', '2026-V3', 'active', 'all,legal,sales'),
            ('PB-IP', '知识产权审查 Playbook', 'saas', 'ip', '公司既有代码、框架、算法、模型、工具链等背景知识产权不得因项目交付自动转让；原则上不承诺交付全部源代码。', '2026-V3', 'active', 'all,legal,sales'),
            ('PB-RENEW', '续约条款 Playbook', 'saas', 'renewal', '原则上采用双方书面确认后续约；若保留自动续约，应设置合理通知期并缩短自动续约周期。', '2026-V3', 'active', 'all,legal,sales'),
            ('PB-JUR', '争议解决 Playbook', 'saas', 'jurisdiction', '优先选择我方所在地或双方可接受的中立争议解决地。客户单方所在地管辖需结合交易规模与谈判地位评估。', '2026-V3', 'active', 'all,legal,sales'),
            ('PB-OLD', '历史责任限制 Playbook', 'saas', 'liability', '历史版本曾允许责任上限为合同金额两倍。该规则已经废弃。', '2025-V1', 'inactive', 'all,legal,sales'),
        ]
        conn.executemany('INSERT INTO playbooks VALUES (?,?,?,?,?,?,?,?)', playbooks)
        contracts = [
            _contract('CT-SAAS-STD', '标准 SaaS 服务合同', 'saas', 'V1', '标准SaaS合同：付款30天；责任上限为合同金额；背景知识产权保留；不自动续约；双方合理终止。', 300000),
            _contract('CT-SALES-180', '客户销售合同-180天付款', 'sales', 'V1', '客户销售合同：最终客户验收后180天付款；其他条款接近公司标准。', 800000),
            _contract('CT-SAAS-CRITICAL', '客户定制 SaaS 合同-无限责任', 'saas', 'V1', '客户要求乙方承担无限责任，并要求交付全部源代码、底层算法及相关知识产权。', 1200000),
            _contract('CT-SAAS-RENEW', '渠道 SaaS 合同-自动续约', 'saas', 'V1', '合同到期前60天未提出异议则自动续约36个月。', 500000),
            _contract('CT-SAAS-V1', 'Phoenix SaaS 合同 V1', 'saas', 'V1', 'Phoenix合同V1：付款30天；责任上限为合同总金额；背景知识产权保留。', 900000),
            _contract('CT-SAAS-V2', 'Phoenix SaaS 合同 V2', 'saas', 'V2', 'Phoenix合同V2：付款30天；责任上限改为乙方承担无限责任；背景知识产权保留。', 900000, 'CT-SAAS-V1'),
        ]
        conn.executemany('INSERT INTO contracts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', contracts)
        clause_rows = []

        def add(cid, ctype, title, content, norm, order):
            clause_rows.append((f'{cid}-{ctype}', cid, ctype, title, content, jdump(norm), order))

        for i, (ct, (norm, text)) in enumerate(STANDARD.items(), 1):
            add('CT-SAAS-STD', ct, ct, text, norm, i)
        add('CT-SALES-180', 'payment', '付款条款', '乙方完成验收且甲方最终客户确认后180日内付款。', {'payment_days': 180, 'payment_trigger': 'final_customer_acceptance'}, 1)
        for i, ct in enumerate(['liability', 'ip', 'renewal', 'termination', 'jurisdiction'], 2):
            norm, text = STANDARD[ct]
            add('CT-SALES-180', ct, ct, text, norm, i)
        add('CT-SAAS-CRITICAL', 'payment', '付款条款', STANDARD['payment'][1], STANDARD['payment'][0], 1)
        add('CT-SAAS-CRITICAL', 'liability', '责任条款', '乙方对甲方因本合同产生的全部损失承担无限责任。', {'liability_cap': 'unlimited'}, 2)
        add('CT-SAAS-CRITICAL', 'ip', '知识产权', '乙方应向甲方交付全部源代码、算法和技术资料，全部背景知识产权归甲方所有。', {'background_ip_owner': 'customer', 'source_code_delivery': True}, 3)
        for i, ct in enumerate(['renewal', 'termination', 'jurisdiction'], 4):
            norm, text = STANDARD[ct]
            add('CT-SAAS-CRITICAL', ct, ct, text, norm, i)
        for i, ct in enumerate(['payment', 'liability', 'ip'], 1):
            norm, text = STANDARD[ct]
            add('CT-SAAS-RENEW', ct, ct, text, norm, i)
        add('CT-SAAS-RENEW', 'renewal', '自动续约', '若任一方未在到期前60日书面提出终止，则合同自动续约36个月。', {'auto_renewal': True, 'renewal_months': 36, 'notice_days': 60}, 4)
        for i, ct in enumerate(['termination', 'jurisdiction'], 5):
            norm, text = STANDARD[ct]
            add('CT-SAAS-RENEW', ct, ct, text, norm, i)
        for i, ct in enumerate(['payment', 'liability', 'ip', 'renewal', 'termination', 'jurisdiction'], 1):
            norm, text = STANDARD[ct]
            add('CT-SAAS-V1', ct, ct, text, norm, i)
        add('CT-SAAS-V2', 'payment', '付款条款', STANDARD['payment'][1], STANDARD['payment'][0], 1)
        add('CT-SAAS-V2', 'liability', '责任条款', '乙方对本合同项下任何损失承担无限责任。', {'liability_cap': 'unlimited'}, 2)
        for i, ct in enumerate(['ip', 'renewal', 'termination', 'jurisdiction'], 3):
            norm, text = STANDARD[ct]
            add('CT-SAAS-V2', ct, ct, text, norm, i)
        conn.executemany('INSERT INTO clauses VALUES (?,?,?,?,?,?,?)', clause_rows)
        conn.executemany('INSERT INTO bad_cases VALUES (?,?,?,?,?)', [
            ('BC-001', '旧版 Playbook 被误召回', 'retrieval', 'open', '检查 status=active 与 version metadata filter。'),
            ('BC-002', '长合同漏掉责任限制条款', 'clause_extraction', 'open', '按条款结构切分，并增加关键条款 completeness check。'),
            ('BC-003', '客户 V2 只改一条却整份重审', 'cost', 'fixed', '通过 parent_version + normalized clause diff 做增量审查。'),
        ])
