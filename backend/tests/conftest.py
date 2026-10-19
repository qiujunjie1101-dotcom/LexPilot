from __future__ import annotations

import os
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1]
TEST_DB = BACKEND_ROOT / 'tests' / 'test_legal_agent.db'

os.environ['MOCK_MODE'] = 'true'
os.environ['DATABASE_PATH'] = str(TEST_DB)
os.environ['DEEPSEEK_API_KEY'] = ''
os.environ['CORS_ORIGINS'] = 'http://localhost:5173,http://localhost:3000'

from contract_reviewer.infrastructure.database import db_path  # noqa: E402
from contract_reviewer.services.seed_service import seed  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    path = str(db_path())
    for suffix in ('', '-wal', '-shm'):
        Path(path + suffix).unlink(missing_ok=True)
    seed(True)
    yield
