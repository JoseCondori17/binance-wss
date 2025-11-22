import asyncio

from binance_wss.extract.binance_client import extract_all          # ETL: Extract
from binance_wss.transform.kline_processor import transform_merge     # ETL: Transform
from binance_wss.load.mongo_loader import load_to_mongo                  # ETL: Load
from binance_wss.main import init_db                        # inicializa Beanie + Mongo


async def main():
    #Inicializar conexión a Mongo y modelos Beanie
    await init_db()

    #EXTRACT: traer datos de Binance (klines + aggtrades)
    data = extract_all()   # {'klines': DataFrame, 'aggtrades': lista de DataFrames}

    #TRANSFORM: castear tipos, unir klines con aggtrades
    merged_df = transform_merge(data)

    print("Filas del DataFrame final:", merged_df.height)
    print(merged_df.head())
    #print(merged_df.head(10))
    
    #LOAD: insertar en MongoDB
    await load_to_mongo(merged_df)

    print("datos cargados en MongoDB :b")


if __name__ == "__main__":
    asyncio.run(main())
