from __future__ import annotations
from dataclasses import dataclass
from fastapi import Header, HTTPException
from .db import row

@dataclass(frozen=True)
class SecurityContext:
    user_id: str; role: str; department_id: str; groups: tuple[str, ...]; tenant_id: str = 'TENANT-DEMO'

def get_security_context(x_user_id: str = Header(default='sales-001'), x_role: str = Header(default='sales'), x_department_id: str = Header(default='sales-east'), x_groups: str = Header(default='all,sales')) -> SecurityContext:
    return SecurityContext(x_user_id, x_role, x_department_id, tuple(x.strip() for x in x_groups.split(',') if x.strip()))

def ensure_contract_access(contract_id: str, ctx: SecurityContext) -> dict:
    contract = row('SELECT * FROM contracts WHERE id=?', (contract_id,))
    if not contract: raise HTTPException(status_code=404, detail='CONTRACT_NOT_FOUND')
    if ctx.role in {'legal','legal_admin'} or contract['owner_user_id'] == ctx.user_id or (ctx.role == 'department_manager' and contract['department_id'] == ctx.department_id): return contract
    raise HTTPException(status_code=403, detail='CONTRACT_ACCESS_DENIED')

def ensure_legal_reviewer(ctx: SecurityContext) -> None:
    if ctx.role not in {'legal','legal_admin'}: raise HTTPException(status_code=403, detail='LEGAL_REVIEW_PERMISSION_REQUIRED')
