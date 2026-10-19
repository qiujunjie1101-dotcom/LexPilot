"""FastAPI 依赖注入容器：安全主体、配置、仓储与领域服务实例。"""
from __future__ import annotations

from typing import Any, Callable

from fastapi import Header, HTTPException

from ..common.constants import LEGAL_ROLES
from ..common.security import SecurityContext
from ..config import Settings, settings
from ..infrastructure.repositories.bad_case_repository import BadCaseRepository, bad_case_repository
from ..infrastructure.repositories.contract_repository import contract_repository
from ..services.contract_service import ContractService, contract_service
from ..services.knowledge_service import KnowledgeService, knowledge_service
from ..services.legal_review_service import LegalReviewService, legal_review_service
from ..workflow.graph import run_review


def get_settings() -> Settings:
    return settings


def get_security_context(
    x_user_id: str = Header(default='sales-001'),
    x_role: str = Header(default='sales'),
    x_department_id: str = Header(default='sales-east'),
    x_groups: str = Header(default='all,sales'),
) -> SecurityContext:
    return SecurityContext(x_user_id, x_role, x_department_id, tuple(item.strip() for item in x_groups.split(',') if item.strip()))


def ensure_contract_access(contract_id: str, ctx: SecurityContext) -> dict[str, Any]:
    contract = contract_repository.get(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail='CONTRACT_NOT_FOUND')
    if ctx.role in LEGAL_ROLES or contract['owner_user_id'] == ctx.user_id or (ctx.role == 'department_manager' and contract['department_id'] == ctx.department_id):
        return contract
    raise HTTPException(status_code=403, detail='CONTRACT_ACCESS_DENIED')


def ensure_legal_reviewer(ctx: SecurityContext) -> None:
    if ctx.role not in LEGAL_ROLES:
        raise HTTPException(status_code=403, detail='LEGAL_REVIEW_PERMISSION_REQUIRED')


def ensure_legal_admin(ctx: SecurityContext) -> None:
    if ctx.role not in LEGAL_ROLES:
        raise HTTPException(403, 'LEGAL_ADMIN_REQUIRED')


def get_contract_service() -> ContractService:
    return contract_service


def get_knowledge_service() -> KnowledgeService:
    return knowledge_service


def get_legal_review_service() -> LegalReviewService:
    return legal_review_service


def get_bad_case_repository() -> BadCaseRepository:
    return bad_case_repository


def get_review_runner() -> Callable[[str, SecurityContext], dict[str, Any]]:
    return run_review
