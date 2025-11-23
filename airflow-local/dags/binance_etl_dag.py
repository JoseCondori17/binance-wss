from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from binance_wss.data.extract import extract_all
from binance_wss.data.transform import transform_merge
from binance_wss.data.load import load_to_mongo_task 


with DAG(
    dag_id="binance_klines_to_mongo",
    start_date=datetime(2025, 11, 17),
    schedule="@hourly",
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_all,  # devuelve algo JSON-serializable
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_merge,  # también devuelve algo JSON-serializable
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_to_mongo_task,  # wrapper síncrono
    )

    extract >> transform >> load
