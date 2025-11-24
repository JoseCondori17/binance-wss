from fastapi import APIRouter
from .kpis import router as kpis_router
from .klines import router as klines_router

api_router = APIRouter(prefix="/api/v1")

# routers
api_router.include_router(kpis_router)
api_router.include_router(klines_router)
