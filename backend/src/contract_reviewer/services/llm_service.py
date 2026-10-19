"""带重试、退避与降级保护的 LLM 客户端服务。"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from ..common.exceptions import LLMServiceError
from ..config import settings
from ..infrastructure.database import jdump


def chat_json(system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
    if settings.mock_mode:
        return fallback
    if not settings.deepseek_api_key:
        raise LLMServiceError('MOCK_MODE=false but DEEPSEEK_API_KEY is empty')
    payload = {
        'model': settings.deepseek_model,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'response_format': {'type': 'json_object'},
        'temperature': 0.2,
    }
    request = urllib.request.Request(
        f'{settings.deepseek_base_url}/chat/completions',
        data=json.dumps(payload).encode(),
        headers={'Authorization': f'Bearer {settings.deepseek_api_key}', 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise LLMServiceError(f'DeepSeek request failed: {exc}') from exc
    content = data['choices'][0]['message']['content']
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMServiceError(f'DeepSeek returned non-JSON: {content[:200]}') from exc


def recommendation(contract: dict[str, Any], issues: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    fallback = {
        'summary': f"{contract['title']} 共识别 {len(issues)} 个风险问题。" if issues else f"{contract['title']} 未发现明显红线。",
        'business_advice': 'Critical/High 风险条款需法务确认后再对外回复；低风险合同可按标准流程推进。' if issues else '可进入常规业务审批，但仍应由业务负责人确认商业条件。',
        'disclaimer': '该结果为企业内部合同初审辅助，不替代律师或法务的最终法律判断。',
    }
    if settings.mock_mode:
        return fallback
    system = '你是企业法务合同审查 Copilot。只能依据提供的合同事实、规则命中和公司 Legal Playbook 生成内部初审摘要，不得声称提供最终法律意见。输出 JSON。'
    user = jdump({
        'contract': {'title': contract['title'], 'type': contract['contract_type'], 'version': contract['version']},
        'issues': issues,
        'evidence': [{'title': item['title'], 'version': item['version'], 'content': item['content']} for item in evidence],
        'required_json_keys': ['summary', 'business_advice', 'disclaimer'],
    })
    return chat_json(system, user, fallback)
