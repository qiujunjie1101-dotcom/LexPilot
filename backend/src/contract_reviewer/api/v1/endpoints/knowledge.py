"""法律规约、标准条款模板与企业标准手册（Playbook）管理接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....services.knowledge_service import KnowledgeService
from ...dependencies import get_knowledge_service, get_security_context

router = APIRouter(tags=['knowledge'])


@router.get('/templates')
def templates(
    ctx: SecurityContext = Depends(get_security_context),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return service.list_templates()


@router.get('/playbooks')
def playbooks(
    ctx: SecurityContext = Depends(get_security_context),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    return service.list_playbooks(ctx)
