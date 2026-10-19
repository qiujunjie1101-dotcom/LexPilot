"""评测基准运行触发与指标报表查询接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....services import evaluation_service
from ...dependencies import get_security_context

router = APIRouter(tags=['evaluations'])


@router.get('/eval/cases')
def eval_cases(ctx: SecurityContext = Depends(get_security_context)):
    return evaluation_service.CASES


@router.post('/eval/run')
def eval_run(ctx: SecurityContext = Depends(get_security_context)):
    return evaluation_service.run_eval()
