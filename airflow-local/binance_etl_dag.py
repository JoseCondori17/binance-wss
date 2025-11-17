from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from binance_wss.extract import extract_all
from binance_wss.transform import transform_merge
from binance_wss.load import save_to_mongo

with DAG(
    dag_id="binance_klines_to_mongo",
    start_date=datetime(2025, 11, 17),
    schedule="@hourly",
    catchup=False,
) as dag:

    extract = PythonOperator(task_id="extract", python_callable=extract_all)
    transform = PythonOperator(task_id="transform", python_callable=transform_merge)
    load = PythonOperator(task_id="load", python_callable=save_to_mongo)

    extract >> transform >> load