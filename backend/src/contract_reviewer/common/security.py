"""安全主体（Security Principal）上下文，供 API 与领域层共用。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecurityContext:
    user_id: str
    role: str
    department_id: str
    groups: tuple[str, ...]
    tenant_id: str = 'TENANT-DEMO'
