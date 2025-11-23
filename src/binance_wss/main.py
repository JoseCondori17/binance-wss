from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from binance_wss.app.config import settings
from binance_wss.models.mongo_models import Kline


async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    await init_beanie(
        database=db,
        document_models=[Kline],
    )
