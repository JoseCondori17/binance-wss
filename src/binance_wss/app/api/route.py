from fastapi import APIRouter
from .kpis import router as kpis_router

api_router = APIRouter(prefix="/api/v1")

# Incluir routers
api_router.include_router(kpis_router)
