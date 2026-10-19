"""法规标准、标准条款模板与 Legal Playbook 维护服务。"""
from __future__ import annotations

from typing import Any

from ..common.security import SecurityContext
from ..infrastructure.database import jload
from ..infrastructure.repositories.knowledge_repository import knowledge_repository


class KnowledgeService:
    def load_template(self, contract_type: str) -> dict[str, dict[str, Any]]:
        template: dict[str, dict[str, Any]] = {}
        for item in knowledge_repository.standard_clauses_for(contract_type):
            item['normalized'] = jload(item.pop('normalized_json'), {})
            template[item['clause_type']] = item
        return template

    def list_templates(self) -> list[dict[str, Any]]:
        return knowledge_repository.active_standard_clauses()

    def is_visible(self, playbook: dict[str, Any], ctx: SecurityContext) -> bool:
        acl = {item.strip() for item in playbook['acl_groups'].split(',') if item.strip()}
        return 'all' in acl or bool(acl.intersection(ctx.groups)) or ctx.role in acl

    def filter_visible(self, playbooks: list[dict[str, Any]], ctx: SecurityContext) -> list[dict[str, Any]]:
        return [playbook for playbook in playbooks if self.is_visible(playbook, ctx)]

    def list_playbooks(self, ctx: SecurityContext) -> list[dict[str, Any]]:
        return self.filter_visible(knowledge_repository.active_playbooks(), ctx)


knowledge_service = KnowledgeService()
