from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import MongoDsn

class Settings(BaseSettings):
    BINANCE_API_KEY: str
    BINANCE_API_SECRET_KEY: str
    BINANCE_API_BASE_URL: str

    MONGODB_URI: MongoDsn
    MONGODB_DB_NAME: str
    MONGODB_COLLECTION_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

print(settings.model_dump())