"""Milvus 向量数据库适配的抽象与本地实现（当前集合为内存态，可切换 Milvus 后端）。"""
from __future__ import annotations

from typing import Any

from . import embedding


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class InMemoryVectorStore:
    def search(self, query_vector: list[float], documents: list[dict[str, Any]], top_k: int | None = None) -> list[dict[str, Any]]:
        ranked = sorted(
            documents,
            key=lambda doc: cosine(query_vector, embedding.hash_vector(doc['content'])),
            reverse=True,
        )
        return ranked if top_k is None else ranked[:top_k]


vector_store = InMemoryVectorStore()
