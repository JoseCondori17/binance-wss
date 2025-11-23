# binance_wss/load/mongo_loader.py

import asyncio

from datetime import datetime, timezone
from binance_wss.app.db import init_db
from binance_wss.app.models.mongo_models import Kline


def to_datetime_ms(value):
    """
    Convierte milisegundos desde epoch (int/float) a datetime UTC.
    Si ya viene como datetime, lo devuelve tal cual.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        # Binance usa milisegundos desde epoch (UTC)
        return datetime.fromtimestamp(value / 1000.0, tz=timezone.utc)
    raise TypeError(f"No se puede convertir a datetime: {value} ({type(value)})")


def load_to_mongo_task(**context):
    """
    Wrapper síncrono que llama Airflow.
    Ejecuta la corrutina load_to_mongo dentro de un event loop propio.
    """
    asyncio.run(load_to_mongo(**context))


async def load_to_mongo(**context):
    """
    Task de carga (L de ETL):
    - Inicializa la conexión a Mongo/Beanie.
    - Lee del XCom lo que devolvió el task 'transform' (lista[dict]).
    - Construye instancias de Kline y las inserta en la colección.
    """
    # Inicializar Mongo + Beanie en este proceso del task
    await init_db()

    ti = context["ti"]
    rows = ti.xcom_pull(task_ids="transform")  # se espera lista[dict]

    if not rows:
        return

    records: list[Kline] = []

    for row in rows:
        # Convertir open_time y close_time a datetime (si vienen en ms)
        open_time = to_datetime_ms(row["open_time"])
        close_time = to_datetime_ms(row["close_time"])

        kline_data = {
            "open_time": open_time,
            "close_time": close_time,
            "symbol": "BTCUSDT",  # modify
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
        }

        # Por ahora sin aggtrades; si en el futuro el transform te devuelve
        # una lista de dicts de aggtrades, aquí construirías objetos AggTrade.
        kline_data["aggtrades"] = []  # list[AggTrade]

        records.append(Kline(**kline_data))

    if records:
        await Kline.insert_many(records)
