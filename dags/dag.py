import logging
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from airflow.decorators import dag, task
from datetime import datetime

from utils import fetch_all_weather_data
from transform import enrich_customers, run_first_validations, run_second_validations

logger = logging.getLogger(__name__)

SOURCE_DB_PATH = os.environ.get("SQLITE_SRC_PATH", "/opt/airflow/data/northwind.db")
DEST_DB_PATH = os.environ.get(
    "POSTGRES_DEST_CONN", "postgresql://airflow:airflow@postgres-dest/airflow"
)
CUSTOMERS_TABLE_NAME = "customers"
ORDERS_TABLE_NAME = "orders"
REGION_MAPPING_FILE_NAME = "region_mapping_DE.xlsx"
REGION_MAPPING_NAME = "region_mapping"
WEATHER_DATA_NAME = "weather_data"
DATA_DIR = "/opt/airflow/data"


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def extract(**context):
        # Load customers and orders data from SQLite
        conn = sqlite3.connect(SOURCE_DB_PATH)
        customers_df = pd.read_sql(f"SELECT * FROM {CUSTOMERS_TABLE_NAME}", conn)
        customers_path = (
            f"{DATA_DIR}/extract_{CUSTOMERS_TABLE_NAME}_{context['run_id']}.parquet"
        )
        customers_df.to_parquet(customers_path, index=False)

        orders_df = pd.read_sql(f"SELECT * FROM {ORDERS_TABLE_NAME}", conn)
        orders_path = (
            f"{DATA_DIR}/extract_{ORDERS_TABLE_NAME}_{context['run_id']}.parquet"
        )
        orders_df.to_parquet(orders_path, index=False)
        conn.close()

        # Load region mapping data from Excel
        region_mapping_df = pd.read_excel(f"{DATA_DIR}/{REGION_MAPPING_FILE_NAME}")
        region_mapping_path = (
            f"{DATA_DIR}/extract_{REGION_MAPPING_NAME}_{context['run_id']}.parquet"
        )
        region_mapping_df.to_parquet(region_mapping_path, index=False)

        # Fetch weather data for specified cities
        cities = customers_df["City"].unique().tolist()
        weather_data_df = fetch_all_weather_data(cities)
        weather_data_path = (
            f"{DATA_DIR}/extract_{WEATHER_DATA_NAME}_{context['run_id']}.parquet"
        )
        weather_data_df.to_parquet(weather_data_path, index=False)

        return {
            "customers": customers_path,
            "orders": orders_path,
            "region_mapping": region_mapping_path,
            "weather_data": weather_data_path,
        }

    @task
    def transform(**context):
        data_paths = context["ti"].xcom_pull(task_ids="extract")

        # Read the extracted data from parquet files
        customers_df = pd.read_parquet(data_paths["customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        region_mapping_df = pd.read_parquet(data_paths["region_mapping"])

        # Run first validations on the extracted data
        run_first_validations(
            customers_df=customers_df,
            orders_df=orders_df,
            region_mapping_df=region_mapping_df,
        )
        # Run enrichment on customers data
        enriched_customers_df = enrich_customers(
            customers_df, pd.read_parquet(data_paths["weather_data"]), region_mapping_df
        )
        # Run second validations on the enriched customers data
        run_second_validations(enriched_customers_df=enriched_customers_df)

        enrich_customers_path = (
            f"{DATA_DIR}/enriched_customers_{context['run_id']}.parquet"
        )
        enriched_customers_df.to_parquet(enrich_customers_path, index=False)

        return {
            "enriched_customers": enrich_customers_path,
            "orders": data_paths["orders"],
            "region_mapping": data_paths["region_mapping"],
        }

    @task
    def load(**context):
        data_paths = context["ti"].xcom_pull(task_ids="transform")
        enriched_customers_df = pd.read_parquet(data_paths["enriched_customers"])
        orders_df = pd.read_parquet(data_paths["orders"])
        region_mapping_df = pd.read_parquet(data_paths["region_mapping"])

        # Load the enriched customers, orders, and region mapping data into PostgreSQL
        engine = create_engine(DEST_DB_PATH)
        enriched_customers_df.to_sql(
            "enriched_customers", engine, if_exists="replace", index=False
        )
        orders_df.to_sql("orders", engine, if_exists="replace", index=False)
        region_mapping_df.to_sql(
            "region_mapping", engine, if_exists="replace", index=False
        )

    @task(trigger_rule="all_done")
    def cleanup():
        parquet_files = [
            os.path.join(DATA_DIR, file_name)
            for file_name in os.listdir(DATA_DIR)
            if file_name.endswith(".parquet")
        ]

        for parquet_file in parquet_files:
            os.remove(parquet_file)
            logger.info("Removed temporary parquet file: %s", parquet_file)

    extract() >> transform() >> load() >> cleanup()


northwind_etl()
