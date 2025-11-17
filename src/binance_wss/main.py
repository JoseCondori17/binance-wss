import asyncio
from beanie import init_beanie
from pymongo import AsyncMongoClient

from config.settings import settings
from load.mongo_loader import Kline, AggTrade

async def init_db():
    client = AsyncMongoClient(settings.MONGODB_URI)
    database = client[settings.MONGODB_DB_NAME]
    await init_beanie(
        database=database, 
        document_models=[Kline, AggTrade]
    )

if __name__ == "__main__":
    asyncio.run(init_db())