from airflow.decorators import dag, task
from datetime import datetime
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os

SOURCE_DB_PATH = os.environ.get("SQLITE_SRC_PATH", "/opt/airflow/data/northwind.db")
DEST_DB_PATH = os.environ.get(
    "POSTGRES_DEST_CONN", "postgresql://airflow:airflow@postgres-dest/airflow"
)
REGION_MAPPING_FILE_NAME = "region_mapping_DE.xlsx"
SQLITE_TABLE_NAMES = ["customers", "orders"]
REGION_MAPPING_TABLE_NAME = "region_mapping"
DATA_DIR = "/opt/airflow/data"


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def load_region_mapping():
        region_mapping_path = f"{DATA_DIR}/{REGION_MAPPING_FILE_NAME}"
        region_mapping_df = pd.read_excel(region_mapping_path)
        engine = create_engine(DEST_DB_PATH)
        region_mapping_df.to_sql(
            REGION_MAPPING_TABLE_NAME, engine, if_exists="replace", index=False
        )

    @task
    def extract(**context):
        table_data_path_mapping = {}

        conn = sqlite3.connect(SOURCE_DB_PATH)
        for table_name in SQLITE_TABLE_NAMES:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            path = f"{DATA_DIR}/extract_{table_name}_{context['run_id']}.parquet"
            df.to_parquet(path, index=False)
            table_data_path_mapping[table_name] = path
        conn.close()

        engine = create_engine(DEST_DB_PATH)
        region_mapping_df = pd.read_sql(f"SELECT * FROM {REGION_MAPPING_TABLE_NAME}", engine)
        region_mapping_path = (
            f"{DATA_DIR}/extract_{REGION_MAPPING_TABLE_NAME}_{context['run_id']}.parquet"
        )
        region_mapping_df.to_parquet(region_mapping_path, index=False)
        table_data_path_mapping[REGION_MAPPING_TABLE_NAME] = region_mapping_path

        return table_data_path_mapping

    @task
    def transform(**context):
        data_paths = context["ti"].xcom_pull(task_ids="extract")
        customers_df = pd.read_parquet(data_paths["customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        # transformation logic here
        customers_path = f"{DATA_DIR}/transform_customers_{context['run_id']}.parquet"
        customers_df.to_parquet(customers_path, index=False)
        orders_path = f"{DATA_DIR}/transform_orders_{context['run_id']}.parquet"
        orders_df.to_parquet(orders_path, index=False)

        return {"customers": customers_path, "orders": orders_path}

    @task
    def load(**context):
        data_paths = context["ti"].xcom_pull(task_ids="transform")
        customers_df = pd.read_parquet(data_paths["customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        engine = create_engine(DEST_DB_PATH)
        customers_df.to_sql("customers", engine, if_exists="replace", index=False)
        orders_df.to_sql("orders", engine, if_exists="replace", index=False)

    load_region_mapping() >> extract() >> transform() >> load()


northwind_etl()
