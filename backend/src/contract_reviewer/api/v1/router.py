"""路由聚合入口：统一挂载各子路由端点。"""
from __future__ import annotations

from fastapi import APIRouter

from .endpoints import bad_cases, contracts, evaluations, knowledge, legal_reviews, reviews, rules

api_router = APIRouter()
api_router.include_router(contracts.router)
api_router.include_router(reviews.router)
api_router.include_router(legal_reviews.router)
api_router.include_router(knowledge.router)
api_router.include_router(rules.router)
api_router.include_router(evaluations.router)
api_router.include_router(bad_cases.router)
