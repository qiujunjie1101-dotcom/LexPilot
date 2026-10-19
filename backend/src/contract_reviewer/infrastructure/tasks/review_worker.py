"""审查任务 worker 入口：同步编排逻辑的异步调度适配点。"""
from __future__ import annotations

from typing import Any

from ...common.security import SecurityContext


def run_review_task(contract_id: str, ctx: SecurityContext) -> dict[str, Any]:
    from ...workflow.graph import run_review

    return run_review(contract_id, ctx)
