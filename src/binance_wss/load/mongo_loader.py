import pymongo
import polars as pl

from beanie import Document
from pydantic import BaseModel

class AggTrade(Document):
    trade_id: int
    price: float
    quantity: float
    first_trade_id: int
    last_trade_id: int
    timestamp: int
    is_buyer_maker: bool
    is_best_match: bool

    class Settings:
        name = "aggtrades"
        indexes = [
            "trade_id",
            "timestamp"
        ]

class Kline(Document):
    open_time: int
    close_time: int
    symbol: str
    interval: str
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: float
    aggtrades: list[AggTrade] = []

    class Settings:
        name = "kline_with_aggtrades"
        indexes = [
            "open_time",
            [
                ("open_time", pymongo.ASCENDING), 
                ("symbol", pymongo.ASCENDING)
            ],
        ]

async def load_to_mongo(data: pl.DataFrame):
    records = []
    
    for row in data.iter_rows(named=True):
        kline_data = {
            "open_time": row["open_time"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
            "close_time": row["close_time"],
            "quote_asset_volume": row["quote_asset_volume"],
            "number_of_trades": row["number_of_trades"],
            "taker_buy_base_asset_volume": row["taker_buy_base_asset_volume"],
            "taker_buy_quote_asset_volume": row["taker_buy_quote_asset_volume"],
        }

        aggtrades_list = row["aggtrades"]
        if aggtrades_list is not None:
            aggtrades = [
                AggTrade(
                    agg_trade_id=t["agg_trade_id"],
                    price=t["price"],
                    quantity=t["quantity"],
                    first_trade_id=t["first_trade_id"],
                    last_trade_id=t["last_trade_id"],
                    timestamp=t["timestamp"],
                    is_buyer_maker=t["is_buyer_maker"],
                    is_best_match=t["is_best_match"],
                ).model_dump()
                for t in aggtrades_list
            ]
        else:
            aggtrades = []

        kline_data["aggtrades"] = aggtrades
        records.append(Kline(**kline_data))

        await Kline.insert_many(records)