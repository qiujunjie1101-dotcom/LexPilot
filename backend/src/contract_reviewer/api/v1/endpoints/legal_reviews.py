"""法务人工复核工作流接口（审批 / 驳回）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ....common.security import SecurityContext
from ....schemas.requests import LegalDecisionRequest
from ....services.legal_review_service import LegalReviewService
from ...dependencies import ensure_legal_reviewer, get_legal_review_service, get_security_context

router = APIRouter(prefix='/legal-reviews', tags=['legal-reviews'])


@router.get('')
def legal_reviews(
    ctx: SecurityContext = Depends(get_security_context),
    service: LegalReviewService = Depends(get_legal_review_service),
):
    ensure_legal_reviewer(ctx)
    return service.list_reviews()


@router.post('/{legal_review_id}/decision')
def legal_review_decision(
    legal_review_id: str,
    request: LegalDecisionRequest,
    ctx: SecurityContext = Depends(get_security_context),
    service: LegalReviewService = Depends(get_legal_review_service),
):
    ensure_legal_reviewer(ctx)
    try:
        return service.decide(legal_review_id, request.decision, request.comment, ctx)
    except KeyError:
        raise HTTPException(404, 'LEGAL_REVIEW_NOT_FOUND')
