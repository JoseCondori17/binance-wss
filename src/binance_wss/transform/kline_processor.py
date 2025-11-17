import polars as pl

def transform_merge(data):
    kline_df: pl.DataFrame = data["klines"]
    aggtrades_list = data["aggtrades"]

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
        pl.col("open_time").cast(pl.Datetime),
        pl.col("close_time").cast(pl.Datetime),
    ])

    # proccess aggtrades
    processed_aggtrades = []
    kline_open_times = []
    for item in aggtrades_list:
        open_time = item["kline_open"]
        agg_df = item["aggtrades"]

        agg_df = agg_df.cast({
            "agg_trade_id": pl.Int64,
            "price": pl.Float64,
            "quantity": pl.Float64,
            "first_trade_id": pl.Int64,
            "last_trade_id": pl.Int64,
            "timestamp": pl.Int64,
            "is_buyer_maker": pl.Boolean,
            "is_best_match": pl.Boolean,
        }).with_columns([
            pl.col("timestamp").cast(pl.Datetime),
        ])

        processed_aggtrades.append(agg_df)
        kline_open_times.append(open_time)

    # create dataframe with kline_open and aggtrades
    agg_struct_df = pl.DataFrame({
        "kline_open": kline_open_times,
        "aggtrades": processed_aggtrades
    }).with_columns([
        pl.col("kline_open").cast(pl.Datetime)
    ])

    result_df = kline_df.join(
        agg_struct_df,
        left_on="open_time",
        right_on="kline_open",
        how="left"
    )

    return result_df