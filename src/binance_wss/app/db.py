from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from .settings import settings
from .models.mongo_models import Kline

def get_connection():
    try:
        client = MongoClient(
            settings.MONGODB_URI,
            server_api=ServerApi("1")
        )
        client.admin.command("ping")
        db = client[settings.MONGODB_DB_NAME]
        return client, db
    except PyMongoError as e:
        print(f"Error connecting to MongoDB: {e}")
        return None, None

async def init_db():
    client = AsyncIOMotorClient(settings.MONGODB_URI, server_api=ServerApi("1"))
    db = client[settings.MONGODB_DB_NAME]

    await init_beanie(database=db, document_models=[Kline])
    print("Beanie MongoDB initialized")
    return db
