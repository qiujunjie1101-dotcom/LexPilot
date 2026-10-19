from __future__ import annotations
import json, urllib.error, urllib.request
from typing import Any
from .config import settings

class DeepSeekError(RuntimeError): pass

def chat_json(system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
    if settings.mock_mode: return fallback
    if not settings.deepseek_api_key: raise DeepSeekError('MOCK_MODE=false but DEEPSEEK_API_KEY is empty')
    payload={'model':settings.deepseek_model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'response_format':{'type':'json_object'},'temperature':0.2}
    req=urllib.request.Request(f'{settings.deepseek_base_url}/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {settings.deepseek_api_key}','Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r: data=json.loads(r.read().decode())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc: raise DeepSeekError(f'DeepSeek request failed: {exc}') from exc
    content=data['choices'][0]['message']['content']
    try: return json.loads(content)
    except json.JSONDecodeError as exc: raise DeepSeekError(f'DeepSeek returned non-JSON: {content[:200]}') from exc
