from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    BINANCE_API_KEY: str
    BINANCE_API_SECRET_KEY: str
    BINANCE_API_BASE_URL: str

    MONGODB_URI: str
    MONGODB_DB_NAME: str
    MONGODB_COLLECTION_NAME: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
    )

settings = Settings()

if __name__ == "__main__":
    print(settings.model_dump())
