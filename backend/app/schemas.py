from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class ContractImportRequest(BaseModel):
    title: str; contract_type: Literal['sales','purchase','saas','nda','channel','dpa']='saas'; content: str=Field(min_length=20); amount: float|None=None; parent_contract_id: str|None=None
class LegalDecisionRequest(BaseModel): decision: Literal['approved','rejected']; comment: str=''
class BadCaseRequest(BaseModel): title: str; category: str; note: str
