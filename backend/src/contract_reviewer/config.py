"""全局配置中心：加载 .env 与环境变量，保持与旧实现完全一致的取值语义。"""
from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict


def _load_env_file() -> None:
    candidates = [Path('../.env'), Path('.env'), Path(__file__).resolve().parents[3] / '.env']
    for path in candidates:
        if not path.exists():
            continue
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    return default if value is None else value.lower() in {'1', 'true', 'yes', 'on'}


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    mock_mode: bool = _bool('MOCK_MODE', True)
    deepseek_api_key: str = os.getenv('DEEPSEEK_API_KEY', '')
    deepseek_base_url: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com').rstrip('/')
    deepseek_model: str = os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-flash')
    database_path: str = os.getenv('DATABASE_PATH', './data/legal_agent.db')
    cors_origins: tuple[str, ...] = tuple(
        x.strip()
        for x in os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
        if x.strip()
    )


settings = Settings()
