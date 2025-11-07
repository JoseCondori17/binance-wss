import polars as pl

def transform_merge(data):
    kline_df: pl.DataFrame = data["klines"]
    aggtrade_df: pl.DataFrame = data["aggtrades"]

    kline_df = kline_df.cast({
        "open_time": pl.Int64,
        "open": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "close": pl.Float64,
        "volume": pl.Float64,
        "close_time": pl.Int64,
        "quote_asset_volume": pl.Float64,
        "number_of_trades": pl.Int64,
        "taker_buy_base_asset_volume": pl.Float64,
        "taker_buy_quote_asset_volume": pl.Float64,
    }).with_columns([
        pl.from_epoch("open_time", time_unit="ms"),
        pl.from_epoch("close_time", time_unit="ms"),
    ])

    aggtrade_df = aggtrade_df.cast({
        "agg_trade_id": pl.Int64,
        "price": pl.Float64,
        "quantity": pl.Float64,
        "first_trade_id": pl.Int64,
        "last_trade_id": pl.Int64,
        "timestamp": pl.Int64,
        "is_buyer_maker": pl.Boolean,
        "is_best_match": pl.Boolean,  
    }).with_columns([
        pl.from_epoch("timestamp", time_unit="ms"),
    ])

    merged_df = kline_df.join_asof(
        aggtrade_df,
        left_on=["open_time", "close_time"],
        right_on="timestamp",
    )

    return merged_df