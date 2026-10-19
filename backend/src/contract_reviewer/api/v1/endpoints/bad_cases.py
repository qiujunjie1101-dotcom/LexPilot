"""线上审查坏例（Bad Case）上报与管理接口。"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....infrastructure.repositories.bad_case_repository import BadCaseRepository
from ....schemas.requests import BadCaseRequest
from ...dependencies import get_bad_case_repository, get_security_context

router = APIRouter(tags=['bad-cases'])


@router.get('/bad-cases')
def bad_cases(
    ctx: SecurityContext = Depends(get_security_context),
    repository: BadCaseRepository = Depends(get_bad_case_repository),
):
    return repository.list_all()


@router.post('/bad-cases')
def add_bad_case(
    request: BadCaseRequest,
    ctx: SecurityContext = Depends(get_security_context),
    repository: BadCaseRepository = Depends(get_bad_case_repository),
):
    bad_case_id = f'BC-{uuid.uuid4().hex[:8]}'
    repository.insert((bad_case_id, request.title, request.category, 'open', request.note))
    return {'id': bad_case_id, **request.model_dump(), 'status': 'open'}
