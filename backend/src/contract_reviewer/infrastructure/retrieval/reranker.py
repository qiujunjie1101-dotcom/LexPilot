"""Cross-Encoder 精排重排模型加载与推理封装（当前为词法+向量加权的轻量精排）。"""
from __future__ import annotations

from typing import Any

from . import bm25_store, embedding, vector_store


def score(query: str, text: str, query_vector: list[float]) -> float:
    return .65 * bm25_store.lexical_score(query, text) + .35 * vector_store.cosine(query_vector, embedding.hash_vector(text))


class WeightedReranker:
    def rerank(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(documents, key=lambda doc: doc['rerank_score'], reverse=True)


reranker = WeightedReranker()
