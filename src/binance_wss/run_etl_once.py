# src/binance_wss/run_etl_once.py

import asyncio
from binance_wss.app.db import init_db
from binance_wss.data.extract import extract_all
from binance_wss.data.transform import transform_merge
from binance_wss.data.load import load_to_mongo

# Clase dummy para simular XCom pull de Airflow
class DummyTI:
    def __init__(self, data_dict):
        self._data = data_dict

    def xcom_pull(self, task_ids):
        # Retorna datos según el task_id que se pide
        # En este caso solo soportamos "extract" y "transform"
        return self._data

async def main():
    # Inicializar Beanie + MongoDB
    await init_db()

    # ---------------- EXTRACT ----------------
    data = extract_all()  # {'klines': DataFrame, 'aggtrades': lista de DataFrames}
    print("Extracted data keys:", data.keys())

    # ---------------- TRANSFORM ----------------
    dummy_extract_ti = DummyTI(data)
    merged_data = transform_merge(ti=dummy_extract_ti)
    print("Number of rows after transform:", len(merged_data))
    print("Sample row:", merged_data[0])

    # ---------------- LOAD ----------------
    dummy_transform_ti = DummyTI(merged_data)
    await load_to_mongo(ti=dummy_transform_ti)
    print("Data successfully loaded into MongoDB ✅")

if __name__ == "__main__":
    asyncio.run(main())
