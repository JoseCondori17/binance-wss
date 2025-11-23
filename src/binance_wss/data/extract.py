import time
import polars as pl
from binance.client import Client
from ..app.settings import settings

client = Client()

def extract_klines(symbol: str, limit: int | None):
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

def extract_all():
    limit = 10
    klines = extract_klines("BTCUSDT", limit)

    result = []
    for row in klines.iter_rows(named=True):
        open_time = row["open_time"]
        close_time = row["close_time"]
        agg_df = extract_aggtrades("BTCUSDT", open_time, close_time, limit)

        result.append({
            "kline_open": int(open_time),
            "aggtrades": agg_df.to_dicts(),  # lista[dict]
        })

    # Lo que se manda por XCom:
    payload = {
        "klines": klines.to_dicts(),  # lista[dict]
        "aggtrades": result,          # lista[dict{kline_open, aggtrades:list[dict]}]
    }
    return payload