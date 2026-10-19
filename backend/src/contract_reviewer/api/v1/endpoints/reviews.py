"""审查触发、结果获取、看板统计与 Trace 查询接口。"""
from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....config import settings
from ....services import audit_service, report_service
from ...dependencies import ensure_contract_access, get_review_runner, get_security_context

router = APIRouter(tags=['reviews'])


@router.post('/contracts/{contract_id}/review')
def contract_review(
    contract_id: str,
    ctx: SecurityContext = Depends(get_security_context),
    runner: Callable[[str, SecurityContext], dict[str, Any]] = Depends(get_review_runner),
):
    ensure_contract_access(contract_id, ctx)
    return runner(contract_id, ctx)


@router.get('/reviews')
def review_list(ctx: SecurityContext = Depends(get_security_context)):
    return report_service.list_reviews()


@router.get('/dashboard')
def dashboard(ctx: SecurityContext = Depends(get_security_context)):
    return report_service.dashboard_stats(settings.mock_mode)


@router.get('/traces/{trace_id}')
def traces(trace_id: str, ctx: SecurityContext = Depends(get_security_context)):
    return audit_service.list_traces(trace_id)
