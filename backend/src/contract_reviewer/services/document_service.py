"""多格式文档文本提取与版式清洗服务。

当前合同正文以结构化文本导入，按 "[clause_type] 正文" 行切分；
PDF / Docx 解析可在 extract_text 中扩展，条款切分逻辑保持不变。
"""
from __future__ import annotations

import re

_CLAUSE_LINE = re.compile(r'^\[(payment|liability|ip|renewal|termination|jurisdiction)\]\s*(.*)$', re.I)


def extract_text(raw: bytes | str) -> str:
    return raw if isinstance(raw, str) else raw.decode('utf-8', errors='ignore')


def split_clauses(content: str) -> list[tuple[str, str]]:
    parsed: list[tuple[str, str]] = []
    for line in [x.strip() for x in content.splitlines() if x.strip()]:
        match = _CLAUSE_LINE.match(line)
        if not match:
            continue
        parsed.append((match.group(1).lower(), match.group(2)))
    return parsed


def fallback_clause(content: str) -> tuple[str, str]:
    return 'payment', content[:1200]
