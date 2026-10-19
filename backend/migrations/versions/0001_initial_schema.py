"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-19
"""
from __future__ import annotations

from alembic import op

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

TABLES = [
    '''CREATE TABLE IF NOT EXISTS contracts (
 id TEXT PRIMARY KEY,title TEXT NOT NULL,contract_type TEXT NOT NULL,version TEXT NOT NULL,parent_contract_id TEXT,
 owner_user_id TEXT NOT NULL,department_id TEXT NOT NULL,status TEXT NOT NULL,amount REAL,content TEXT NOT NULL,content_hash TEXT NOT NULL,created_at TEXT NOT NULL,
 FOREIGN KEY(parent_contract_id) REFERENCES contracts(id))''',
    '''CREATE TABLE IF NOT EXISTS clauses (
 id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,clause_type TEXT NOT NULL,title TEXT NOT NULL,content TEXT NOT NULL,normalized_json TEXT NOT NULL,sort_order INTEGER NOT NULL,
 FOREIGN KEY(contract_id) REFERENCES contracts(id) ON DELETE CASCADE)''',
    '''CREATE TABLE IF NOT EXISTS standard_clauses (
 id TEXT PRIMARY KEY,contract_type TEXT NOT NULL,clause_type TEXT NOT NULL,standard_text TEXT NOT NULL,normalized_json TEXT NOT NULL,version TEXT NOT NULL,status TEXT NOT NULL,
 required INTEGER NOT NULL DEFAULT 1,severity_if_missing TEXT NOT NULL DEFAULT 'medium')''',
    '''CREATE TABLE IF NOT EXISTS playbooks (
 id TEXT PRIMARY KEY,title TEXT NOT NULL,contract_type TEXT NOT NULL,clause_type TEXT NOT NULL,content TEXT NOT NULL,version TEXT NOT NULL,status TEXT NOT NULL,acl_groups TEXT NOT NULL)''',
    '''CREATE TABLE IF NOT EXISTS review_results (
 id TEXT PRIMARY KEY,contract_id TEXT NOT NULL,trace_id TEXT NOT NULL,risk_score INTEGER NOT NULL,risk_level TEXT NOT NULL,legal_review_required INTEGER NOT NULL,status TEXT NOT NULL,
 summary_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(contract_id) REFERENCES contracts(id))''',
    '''CREATE TABLE IF NOT EXISTS legal_reviews (
 id TEXT PRIMARY KEY,review_result_id TEXT NOT NULL,contract_id TEXT NOT NULL,reviewer_role TEXT NOT NULL,status TEXT NOT NULL,comment TEXT,created_at TEXT NOT NULL,updated_at TEXT,
 FOREIGN KEY(review_result_id) REFERENCES review_results(id))''',
    '''CREATE TABLE IF NOT EXISTS trace_events (id INTEGER PRIMARY KEY AUTOINCREMENT,trace_id TEXT NOT NULL,node TEXT NOT NULL,detail_json TEXT NOT NULL,latency_ms INTEGER NOT NULL,created_at TEXT NOT NULL)''',
    '''CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT,trace_id TEXT,contract_id TEXT,actor_id TEXT NOT NULL,action TEXT NOT NULL,detail_json TEXT NOT NULL,created_at TEXT NOT NULL)''',
    '''CREATE TABLE IF NOT EXISTS bad_cases (id TEXT PRIMARY KEY,title TEXT NOT NULL,category TEXT NOT NULL,status TEXT NOT NULL,note TEXT NOT NULL)''',
]

DROP_ORDER = [
    'bad_cases',
    'audit_logs',
    'trace_events',
    'legal_reviews',
    'review_results',
    'playbooks',
    'standard_clauses',
    'clauses',
    'contracts',
]


def upgrade() -> None:
    for ddl in TABLES:
        op.execute(ddl)


def downgrade() -> None:
    for table in DROP_ORDER:
        op.execute(f'DROP TABLE IF EXISTS {table}')
