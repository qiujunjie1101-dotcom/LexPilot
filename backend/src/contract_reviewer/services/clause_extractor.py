"""条款语义识别与结构化参数抽取服务。"""
from __future__ import annotations

import re
from typing import Any


def normalize(clause_type: str, text: str) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    if clause_type == 'payment':
        days = re.search(r'(\d{1,3})\s*天', text)
        normalized = {
            'payment_days': int(days.group(1)) if days else 30,
            'payment_trigger': 'final_customer_acceptance' if '最终客户' in text else 'invoice_received',
        }
    elif clause_type == 'liability':
        normalized = {'liability_cap': 'unlimited' if '无限' in text else 'contract_amount'}
    elif clause_type == 'ip':
        normalized = {
            'background_ip_owner': 'customer' if ('全部' in text and '归甲方' in text) else 'original_owner',
            'source_code_delivery': '源代码' in text,
        }
    elif clause_type == 'renewal':
        months = re.search(r'(\d{1,3})\s*个月', text)
        normalized = {'auto_renewal': '自动续约' in text, 'renewal_months': int(months.group(1)) if months else 0}
    elif clause_type == 'termination':
        normalized = {'unilateral_termination_customer_only': '甲方有权单方' in text}
    elif clause_type == 'jurisdiction':
        normalized = {'jurisdiction': 'customer_location' if '甲方所在地' in text else 'provider_location'}
    return normalized
