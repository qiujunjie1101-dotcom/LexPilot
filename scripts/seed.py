"""初始化演示种子数据。

用法:
    python scripts/seed.py          # 重建演示数据（清空业务表后重新写入）
    python scripts/seed.py --keep   # 仅在库为空时写入种子数据
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'backend' / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contract_reviewer.infrastructure.database import init_db  # noqa: E402
from contract_reviewer.infrastructure.repositories.contract_repository import contract_repository  # noqa: E402
from contract_reviewer.services.seed_service import seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description='初始化合同审查演示种子数据')
    parser.add_argument('--keep', action='store_true', help='库中已有合同时跳过，不覆盖现有数据')
    args = parser.parse_args()

    init_db()
    if args.keep and contract_repository.has_any():
        print('skip: contracts already exist')
        return
    seed(reset=not args.keep)
    print('seeded: contracts / clauses / standard_clauses / playbooks')


if __name__ == '__main__':
    main()
