
import pymongo
from datetime import datetime
from beanie import Document
from pydantic import BaseModel


class AggTrade(BaseModel):
    trade_id: int
    price: float
    quantity: float
    first_trade_id: int
    last_trade_id: int
    timestamp: datetime
    is_buyer_maker: bool
    is_best_match: bool


class Kline(Document):
    open_time: datetime
    close_time: datetime
    symbol: str
    interval: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    aggtrades: list[AggTrade] = []

    class Settings:
        name = "kline_with_aggtrades"
        indexes = [
            "open_time",
            [
                ("open_time", pymongo.ASCENDING),
                ("symbol", pymongo.ASCENDING),
            ],
        ]
