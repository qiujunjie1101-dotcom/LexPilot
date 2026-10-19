"""批量离线回归评测执行器与报表生成脚本。

用法（在仓库根目录）：
    python -m tests.harness.runner
需要 PYTHONPATH 同时包含 backend/src 与 backend。
"""
from __future__ import annotations

import json

from contract_reviewer.services.evaluation_service import run_eval
from contract_reviewer.services.seed_service import seed

from .evaluators.metrics import summarize


def main() -> dict:
    seed(True)
    report = run_eval()
    return {**report, 'metrics': summarize(report)}


if __name__ == '__main__':
    print(json.dumps(main(), ensure_ascii=False, indent=2))
