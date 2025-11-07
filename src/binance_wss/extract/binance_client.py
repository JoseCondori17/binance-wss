import time
import polars as pl

from binance.client import Client

def extract_klines(symbol: str, limit: int | None):
    client = Client()
    interval = Client.KLINE_INTERVAL_1MINUTE
    data = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )

    df = pl.DataFrame(data, schema=[
        "open_time", "open", "high", "low", "close", 
        "volume", "close_time", "quote_asset_volume", 
        "number_of_trades", "taker_buy_base_asset_volume", 
        "taker_buy_quote_asset_volume", "ignore"
    ], orient="row")

    time.sleep(0.2)
    return df

def extract_aggtrades(
    symbol: str, 
    start_time: int | None, 
    end_time: int | None, 
    limit: int | None
):
    client = Client()
    data = client.get_aggregate_trades(
        symbol=symbol,
        startTime=start_time,
        endTime=end_time,
        limit=limit
    )

    df = pl.DataFrame(data).rename({
        "a": "agg_trade_id",
        "p": "price",
        "q": "quantity",
        "f": "first_trade_id",
        "l": "last_trade_id",
        "T": "timestamp",
        "m": "is_buyer_maker",
        "M": "is_best_match"
    })

    time.sleep(0.2)
    return df

# pendiente: extraer todos los agg trades entre un rango de tiempo, haciendo multiples llamadas si es necesario
def extract_all():
    klines = extract_klines("BTCUSDT", 1000)
    start_time = klines[0, "open_time"]
    end_time = klines[-1, "open_time"] + 60_000

    aggtrades = extract_aggtrades("BTCUSDT", start_time, end_time, 1000)
    return {"klines": klines, "aggtrades": aggtrades}