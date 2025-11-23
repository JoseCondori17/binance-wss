# binance_wss/load/mongo_loader.py

import asyncio
import nest_asyncio
import polars as pl

from datetime import datetime, timezone
from binance_wss.app.db import get_db
from binance_wss.app.models.mongo_models import Kline, AggTrade

nest_asyncio.apply()

def to_datetime_ms(value):
    """
    Convierte milisegundos desde epoch (int/float) a datetime UTC.
    Si ya viene como datetime, lo devuelve tal cual.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    raise TypeError(f"Don't convert to datetime: {value} ({type(value)})")

def load_to_mongo_task(**context):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(load_to_mongo(**context))


async def load_to_mongo(**context):
    """
    Task de carga (L de ETL):
    - Inicializa la conexión a Mongo/Beanie.
    - Lee del XCom lo que devolvió el task 'transform' (lista[dict]).
    - Construye instancias de Kline y las inserta en la colección.
    """
    db = await get_db()

    ti = context["ti"]
    rows = ti.xcom_pull(task_ids="transform")

    if not rows:
        return

    records: list[Kline] = []

    for row in rows:
        open_time = to_datetime_ms(row["open_time"])
        close_time = to_datetime_ms(row["close_time"])

        kline_data = {
            "open_time": open_time,
            "close_time": close_time,
            "symbol": str(row["symbol"]),
            "interval": "1m",
            "open_price": float(row["open"]),
            "close_price": float(row["close"]),
            "high_price": float(row["high"]),
            "low_price": float(row["low"]),
            "volume": float(row["volume"]),
            "quote_asset_volume": float(row["quote_asset_volume"]),
            "number_of_trades": int(row["number_of_trades"]),
            "taker_buy_base_asset_volume": float(row["taker_buy_base_asset_volume"]),
            "taker_buy_quote_asset_volume": float(row["taker_buy_quote_asset_volume"]),
            "aggtrades": row.get("aggtrades", [])
        }
        records.append(Kline(**kline_data))

    if records:
        await Kline.insert_many(records)
