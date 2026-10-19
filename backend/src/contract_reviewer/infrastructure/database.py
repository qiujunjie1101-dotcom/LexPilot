"""关系型数据库连接池与会话管理（当前为 SQLite 实现，可替换为 PostgreSQL）。"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from ..config import settings

SCHEMA = r'''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS contracts (
 id TEXT PRIMARY KEY,title TEXT NOT NULL,contract_type TEXT NOT NULL,version TEXT NOT NULL,parent_contract_id TEXT,
 owner_user_id TEXT NOT NULL,department_id TEXT NOT NULL,status TEXT NOT NULL,amount REAL,content TEXT NOT NULL,content_hash TEXT NOT NULL,created_at TEXT NOT NULL,
 FOREIGN KEY(parent_contract_id) REFERENCES contracts(id));
CREATE TABLE IF NOT EXISTS clauses (
 id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,clause_type TEXT NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,normalized_json TEXT NOT NULL,sort_order INTEGER NOT NULL,
 FOREIGN KEY(contract_id) REFERENCES contracts(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS standard_clauses (
 id TEXT PRIMARY KEY,contract_type TEXT NOT NULL,clause_type TEXT NOT NULL,standard_text TEXT NOT NULL,normalized_json TEXT NOT NULL,version TEXT NOT NULL,status TEXT NOT NULL,
 required INTEGER NOT NULL DEFAULT 1,severity_if_missing TEXT NOT NULL DEFAULT 'medium');
CREATE TABLE IF NOT EXISTS playbooks (
 id TEXT PRIMARY KEY,title TEXT NOT NULL,contract_type TEXT NOT NULL,clause_type TEXT NOT NULL,content TEXT NOT NULL,version TEXT NOT NULL,status TEXT NOT NULL,acl_groups TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS review_results (
 id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,trace_id TEXT NOT NULL,risk_score INTEGER NOT NULL,risk_level TEXT NOT NULL,legal_review_required INTEGER NOT NULL,status TEXT NOT NULL,
 summary_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(contract_id) REFERENCES contracts(id));
CREATE TABLE IF NOT EXISTS legal_reviews (
 id TEXT PRIMARY KEY,review_result_id TEXT NOT NULL,contract_id TEXT NOT NULL,reviewer_role TEXT NOT NULL,status TEXT NOT NULL,comment TEXT,created_at TEXT NOT NULL,updated_at TEXT,
 FOREIGN KEY(review_result_id) REFERENCES review_results(id));
CREATE TABLE IF NOT EXISTS trace_events (id INTEGER PRIMARY KEY AUTOINCREMENT,trace_id TEXT NOT NULL,node TEXT NOT NULL,detail_json TEXT NOT NULL,latency_ms INTEGER NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT,trace_id TEXT,contract_id TEXT,actor_id TEXT NOT NULL,action TEXT NOT NULL,detail_json TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS bad_cases (id TEXT PRIMARY KEY,title TEXT NOT NULL,category TEXT NOT NULL,status TEXT NOT NULL,note TEXT NOT NULL);
'''


def db_path() -> Path:
    path = Path(settings.database_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path(), timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def rows(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def row(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with connect() as conn:
        result = conn.execute(sql, params).fetchone()
        return dict(result) if result else None


def execute(sql: str, params: tuple[Any, ...] = ()) -> None:
    with connect() as conn:
        conn.execute(sql, params)


def jdump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def jload(value: str | None, default: Any = None) -> Any:
    return default if value is None else json.loads(value)
