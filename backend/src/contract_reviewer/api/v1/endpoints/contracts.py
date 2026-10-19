"""合同导入、上传、版本链及详情查询接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ....common.security import SecurityContext
from ....schemas.requests import ContractImportRequest
from ....services.contract_service import ContractService
from ...dependencies import ensure_contract_access, get_contract_service, get_security_context

router = APIRouter(prefix='/contracts', tags=['contracts'])


@router.get('')
def list_contracts(
    ctx: SecurityContext = Depends(get_security_context),
    service: ContractService = Depends(get_contract_service),
):
    return service.list_visible(ctx)


@router.get('/{contract_id}')
def contract_detail(
    contract_id: str,
    ctx: SecurityContext = Depends(get_security_context),
    service: ContractService = Depends(get_contract_service),
):
    ensure_contract_access(contract_id, ctx)
    return service.load(contract_id)


@router.post('/import')
def contract_import(
    request: ContractImportRequest,
    ctx: SecurityContext = Depends(get_security_context),
    service: ContractService = Depends(get_contract_service),
):
    return service.import_contract(
        request.title,
        request.contract_type,
        request.content,
        request.amount,
        request.parent_contract_id,
        ctx,
    )
