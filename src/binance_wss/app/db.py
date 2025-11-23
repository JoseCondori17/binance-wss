import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional

from .settings import settings
from .models.mongo_models import Kline

_db_client: Optional[AsyncIOMotorClient] = None
_db_initialized = False

async def get_db():
    global _db_client, _db_initialized

    if not _db_client:
        _db_client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    if not _db_initialized:
        db = _db_client[settings.MONGODB_DB_NAME]
        await init_beanie(database=db, document_models=[Kline])
        _db_initialized = True
        print("Beanie MongoDB initialized (singleton)")

    return _db_client[settings.MONGODB_DB_NAME]