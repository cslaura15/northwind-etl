from airflow.decorators import dag, task
from datetime import datetime
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os

SOURCE_DB_PATH = os.environ.get("SQLITE_SRC_PATH", "/opt/airflow/data/northwind.db")
DEST_DB_PATH = os.environ.get("POSTGRES_DEST_CONN", "postgresql://airflow:airflow@postgres-dest/airflow")
REGION_MAPPING_FILE_NAME = "region_mapping_DE.xlsx"

@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def load_region_mapping():
        region_mapping_path = f"/opt/airflow/data/{REGION_MAPPING_FILE_NAME}"
        region_mapping_df = pd.read_excel(region_mapping_path)
        engine = create_engine(DEST_DB_PATH)
        region_mapping_df.to_sql("region_mapping", engine, if_exists="replace", index=False)
    
    @task
    def extract(**context):
        conn = sqlite3.connect(SOURCE_DB_PATH)
        customers_df = pd.read_sql("SELECT * FROM customers", conn)
        customers_path = f"/opt/airflow/data/extract_customers_{context['run_id']}.parquet"
        customers_df.to_parquet(customers_path, index=False)
        
        orders_df = pd.read_sql("SELECT * FROM orders", conn)
        orders_path = f"/opt/airflow/data/extract_orders_{context['run_id']}.parquet"
        orders_df.to_parquet(orders_path, index=False)
        conn.close()

        engine = create_engine(DEST_DB_PATH)
        region_mapping_df = pd.read_sql("SELECT * FROM region_mapping", engine)
        region_mapping_path = f"/opt/airflow/data/extract_region_mapping_{context['run_id']}.parquet"
        region_mapping_df.to_parquet(region_mapping_path, index=False)

        return {"customers": customers_path, "orders": orders_path, "region_mapping": region_mapping_path}

    @task
    def transform(**context):
        data_paths = context['ti'].xcom_pull(task_ids='extract')
        customers_df = pd.read_parquet(data_paths["customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        # transformation logic here
        customers_path = f"/opt/airflow/data/transform_customers_{context['run_id']}.parquet"
        customers_df.to_parquet(customers_path, index=False)
        orders_path = f"/opt/airflow/data/transform_orders_{context['run_id']}.parquet"
        orders_df.to_parquet(orders_path, index=False)
        
        return {"customers": customers_path, "orders": orders_path}

    @task
    def load(**context):
        data_paths = context['ti'].xcom_pull(task_ids='transform')
        customers_df = pd.read_parquet(data_paths["customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        engine = create_engine(DEST_DB_PATH)
        customers_df.to_sql("customers", engine, if_exists="replace", index=False)
        orders_df.to_sql("orders", engine, if_exists="replace", index=False)

    load_region_mapping() >> extract() >> transform() >> load()

northwind_etl()