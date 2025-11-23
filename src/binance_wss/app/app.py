"""
Aplicación principal de FastAPI con MongoDB Atlas
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from contextlib import asynccontextmanager

from .models.mongo_models import Kline
from .api.route import api_router
from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=10,
        minPoolSize=1
    )
    
    try:
        await client.admin.command('ping')
    except Exception as e:
        raise
    
    # Inicializar Beanie
    database = client[settings.MONGODB_DB_NAME]
    await init_beanie(
        database=database,
        document_models=[Kline]
    )
    
    app.state.db_client = client
    
    yield
    client.close()


# Crear aplicación FastAPI
app = FastAPI(
    title="Binance WebSocket API",
    description="API para gestionar datos de Binance (Klines y Trades) en MongoDB Atlas",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router)


@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Binance WebSocket API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a MongoDB
        await app.state.db_client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
