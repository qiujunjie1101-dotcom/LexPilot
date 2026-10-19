"""FastAPI 应用入口点：全局中间件、生命周期与路由装配。"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.dependencies import ensure_legal_admin, get_security_context
from .api.v1.router import api_router
from .common.security import SecurityContext
from .config import settings
from .infrastructure.database import init_db
from .infrastructure.repositories.contract_repository import contract_repository
from .services.seed_service import seed
from .workflow.graph import architecture_note


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if not contract_repository.has_any():
        seed(True)
    yield


app = FastAPI(title='Enterprise Legal Contract Review Agent', version='1.0.0', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(api_router, prefix='/api')


@app.get('/health')
def health():
    return {'status': 'ok'}


@app.get('/api/runtime')
def runtime():
    return {
        'mock_mode': settings.mock_mode,
        'deepseek_base_url': settings.deepseek_base_url,
        'deepseek_model': settings.deepseek_model,
        **architecture_note(),
    }


@app.post('/api/admin/seed')
def reseed(ctx: SecurityContext = Depends(get_security_context)):
    ensure_legal_admin(ctx)
    seed(True)
    return {'status': 'seeded'}
