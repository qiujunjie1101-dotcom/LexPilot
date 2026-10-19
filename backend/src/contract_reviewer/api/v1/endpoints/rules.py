"""审查红线规则的查询接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....services import rule_engine
from ...dependencies import get_security_context

router = APIRouter(tags=['rules'])


@router.get('/rules')
def list_rules(ctx: SecurityContext = Depends(get_security_context)):
    return rule_engine.enabled_rules()
