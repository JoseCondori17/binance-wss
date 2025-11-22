import polars as pl

def transform_merge(**context):
    ti = context["ti"]  # get data from xcom
    data = ti.xcom_pull(task_ids="extract")  # dict con "klines" y "aggtrades"

    # KLINES 
    kline_df = pl.DataFrame(data["klines"])

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
    })

    # pasamos de epoch ms → datetime[ms]
    kline_df = kline_df.with_columns(
        pl.col("open_time").cast(pl.Datetime("ms")),
        pl.col("close_time").cast(pl.Datetime("ms")),
    )

    # AGGTRADES
    aggtrades_list = data["aggtrades"]

    processed_aggtrades = []
    kline_open_times = []

    for item in aggtrades_list:
        open_time = item["kline_open"]       # epoch ms
        agg_rows = item["aggtrades"]         # lista[dict]

        agg_df = pl.DataFrame(agg_rows).cast({
            "agg_trade_id": pl.Int64,
            "price": pl.Float64,
            "quantity": pl.Float64,
            "first_trade_id": pl.Int64,
            "last_trade_id": pl.Int64,
            "timestamp": pl.Int64,
            "is_buyer_maker": pl.Boolean,
            "is_best_match": pl.Boolean,
        }).with_columns(
            pl.col("timestamp").cast(pl.Datetime("ms"))
        )

        # guardamos como lista[dict] para poder serializar en XCom / Mongo
        processed_aggtrades.append(agg_df.to_dicts())
        kline_open_times.append(open_time)

    # DataFrame con la estructura por kline
    agg_struct_df = pl.DataFrame({
        "kline_open": kline_open_times,     # epoch ms
        "aggtrades": processed_aggtrades,   # lista[dict]
    }).with_columns(
        pl.col("kline_open").cast(pl.Datetime("ms"))  
    )

    # JOIN
    result_df = kline_df.join(
        agg_struct_df,
        left_on="open_time",
        right_on="kline_open",
        how="left",
    )

    # devolver algo JSON-serializable
    return result_df.to_dicts()
