"""混合检索中枢服务：稠密 + 稀疏召回、RRF 融合与精排。"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from ..common.security import SecurityContext
from ..infrastructure.repositories.knowledge_repository import knowledge_repository
from ..infrastructure.retrieval import bm25_store, embedding, reranker, vector_store
from .knowledge_service import knowledge_service


def search(contract_type: str, clause_type: str, query: str, ctx: SecurityContext, top_k: int = 3) -> list[dict[str, Any]]:
    candidates = knowledge_repository.playbook_candidates(contract_type, clause_type)
    allowed = knowledge_service.filter_visible(candidates, ctx)
    query_vector = embedding.hash_vector(query)
    lexical_ranking = bm25_store.rank(query, allowed)
    vector_ranking = vector_store.vector_store.search(query_vector, allowed)

    scores: dict[str, float] = defaultdict(float)
    documents = {document['id']: document for document in allowed}
    for ranking in (lexical_ranking, vector_ranking):
        for rank, document in enumerate(ranking, 1):
            scores[document['id']] += 1 / (60 + rank)

    results: list[dict[str, Any]] = []
    for document_id in sorted(scores, key=scores.get, reverse=True)[:top_k]:
        item = dict(documents[document_id])
        item['rrf_score'] = round(scores[document_id], 6)
        item['rerank_score'] = round(reranker.score(query, item['content'], query_vector), 4)
        results.append(item)
    return reranker.reranker.rerank(results)
