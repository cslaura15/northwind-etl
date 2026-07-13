import logging
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from airflow.decorators import dag, task
from datetime import datetime

from transform import enrich_customers, run_first_validations, run_second_validations
from utils import (
    get_customers_data,
    get_orders_data,
    get_region_mapping,
    get_weather_data,
    write_to_parquet,
)
from config import DATA_DIR

logger = logging.getLogger(__name__)

SOURCE_DB_PATH = os.environ.get("SQLITE_SRC_PATH", "/opt/airflow/data/northwind.db")
DEST_DB_PATH = os.environ.get(
    "POSTGRES_DEST_CONN", "postgresql://airflow:airflow@postgres-dest/airflow"
)



@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def extract(**context):
        # Load customers and orders data from SQLite
        run_id = context["run_id"]
        conn = sqlite3.connect(SOURCE_DB_PATH)
        
        customers_df = get_customers_data(conn=conn)
        customers_path = write_to_parquet(df=customers_df, table_name='customers', run_id=run_id)
        
        orders_df = get_orders_data(conn=conn)
        orders_path = write_to_parquet(df=orders_df, table_name='orders', run_id=run_id)
        
        conn.close()

        # Load region mapping data from Excel
        region_mapping_df = get_region_mapping()
        region_mapping_path = write_to_parquet(df=region_mapping_df, table_name='region_mapping', run_id=run_id)

        # Fetch weather data for specified cities
        cities = customers_df['City'].unique().tolist()
        logger.info(f"cities: {cities}")
        weather_data_df = get_weather_data(cities=cities)
        logger.info(weather_data_df.head())
        weather_data_path = write_to_parquet(df=weather_data_df, table_name='weather_data', run_id=run_id)

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

        enrich_customers_path = write_to_parquet(
            df=enriched_customers_df, 
            table_name='enriched_customers', 
            run_id=context['run_id']
        )

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

    extract() >> transform() >> load()# >> cleanup()


northwind_etl()
