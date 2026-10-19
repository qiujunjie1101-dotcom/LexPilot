"""BM25 稀疏词法索引（当前以词项覆盖率近似实现，专有名词与法条精准匹配）。"""
from __future__ import annotations

from typing import Any

from . import embedding


def lexical_score(query: str, text: str) -> float:
    query_terms = embedding.tokenize(query)
    text_terms = set(embedding.tokenize(text))
    if not query_terms:
        return 0
    return sum(1 for term in query_terms if term in text_terms) / len(query_terms)


def rank(query: str, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(documents, key=lambda doc: lexical_score(query, doc['content']), reverse=True)
