import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
from airflow.decorators import dag, task
from extract import get_region_mapping, get_sqlite_table, get_weather_data
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
from transform import (clean_and_quarantine, enrich_customers,
                       run_first_validations, run_second_validations)
from utils import get_primary_keys, write_to_parquet

from config import (CUSTOMERS_TABLE_NAME, DATA_DIR, DEST_DB_PATH,
                    ORDERS_TABLE_NAME, REGION_MAPPING_TABLE_NAME,
                    SOURCE_DB_PATH, TABLE_SCHEMA_MAPPING, WEATHER_DATA_NAME)

logger = logging.getLogger(__name__)


@dag(schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["etl"])
def northwind_etl():

    @task
    def extract(**context):
        # Load customers and orders data from SQLite
        run_id = context["run_id"]
        conn = sqlite3.connect(SOURCE_DB_PATH)

        customers_df = get_sqlite_table(table_name=CUSTOMERS_TABLE_NAME, conn=conn)
        customers_path = write_to_parquet(
            df=customers_df,
            table_name=CUSTOMERS_TABLE_NAME,
            run_id=run_id,
            task="extract",
        )

        orders_df = get_sqlite_table(table_name=ORDERS_TABLE_NAME, conn=conn)
        orders_path = write_to_parquet(
            df=orders_df, table_name=ORDERS_TABLE_NAME, run_id=run_id, task="extract"
        )

        conn.close()

        # Load region mapping data from Excel
        region_mapping_df = get_region_mapping()
        region_mapping_path = write_to_parquet(
            df=region_mapping_df,
            table_name=REGION_MAPPING_TABLE_NAME,
            run_id=run_id,
            task="extract",
        )

        # Fetch weather data for specified cities
        cities = customers_df["City"].unique().tolist()
        logger.info(f"cities: {cities}")
        weather_data_df = get_weather_data(cities=cities)
        logger.info(weather_data_df.head())
        weather_data_path = write_to_parquet(
            df=weather_data_df,
            table_name=WEATHER_DATA_NAME,
            run_id=run_id,
            task="extract",
        )

        return {
            CUSTOMERS_TABLE_NAME: customers_path,
            ORDERS_TABLE_NAME: orders_path,
            REGION_MAPPING_TABLE_NAME: region_mapping_path,
            WEATHER_DATA_NAME: weather_data_path,
        }

    @task
    def transform(**context):
        data_paths = context["ti"].xcom_pull(task_ids="extract")
        run_id = context["run_id"]

        # Read the extracted data from parquet files
        customers_df = pd.read_parquet(data_paths[CUSTOMERS_TABLE_NAME])
        orders_df = pd.read_parquet(data_paths[ORDERS_TABLE_NAME])
        logger.info(orders_df.columns)
        region_mapping_df = pd.read_parquet(data_paths[REGION_MAPPING_TABLE_NAME])

        # Run first validations on the extracted data
        run_first_validations(
            customers_df=customers_df,
            orders_df=orders_df,
            region_mapping_df=region_mapping_df,
        )

        # Run cleaning: split each df into valid and quarantine
        # (customers' valid rows aren't written yet - they still need enrichment)
        valid_orders_path, quarantined_orders_path = clean_and_quarantine(
            orders_df, ORDERS_TABLE_NAME, run_id
        )
        valid_region_mapping_path, quarantined_region_mapping_path = (
            clean_and_quarantine(region_mapping_df, REGION_MAPPING_TABLE_NAME, run_id)
        )

        # Run enrichment on customers data
        enriched_customers_df = enrich_customers(
            customers_df=customers_df,
            weather_data_df=pd.read_parquet(data_paths[WEATHER_DATA_NAME]),
            region_mapping_df=region_mapping_df,
        )
        # Run second validations on the enriched customers data
        run_second_validations(enriched_customers_df=enriched_customers_df)
        valid_enriched_customers_path, quarantined_enriched_customers_path = (
            clean_and_quarantine(
                enriched_customers_df, f"enriched_{CUSTOMERS_TABLE_NAME}", run_id
            )
        )

        return {
            CUSTOMERS_TABLE_NAME: valid_enriched_customers_path,
            f"quarantined_{CUSTOMERS_TABLE_NAME}": quarantined_enriched_customers_path,
            ORDERS_TABLE_NAME: valid_orders_path,
            f"quarantined_{ORDERS_TABLE_NAME}": quarantined_orders_path,
            REGION_MAPPING_TABLE_NAME: valid_region_mapping_path,
            f"quarantined_{REGION_MAPPING_TABLE_NAME}": quarantined_region_mapping_path,
        }

    @task
    def load(**context):
        data_paths = context["ti"].xcom_pull(task_ids="transform")

        def _load_table_to_db(path: Path, name: str, engine=sqlite3.Connection):
            records = pd.read_parquet(path).to_dict(orient="records")
            pk_columns = get_primary_keys(schema=TABLE_SCHEMA_MAPPING[name])
            metadata = MetaData()
            table = Table(name, metadata, autoload_with=engine)
            stmt = insert(table).values(records)
            stmt = stmt.on_conflict_do_nothing(index_elements=pk_columns)
            with engine.begin() as conn:
                conn.execute(stmt)

        engine = create_engine(DEST_DB_PATH)
        _load_table_to_db(
            path=data_paths[REGION_MAPPING_TABLE_NAME],
            name=REGION_MAPPING_TABLE_NAME,
            engine=engine,
        )
        data_paths.pop(REGION_MAPPING_TABLE_NAME)
        _load_table_to_db(
            path=data_paths[CUSTOMERS_TABLE_NAME],
            name=CUSTOMERS_TABLE_NAME,
            engine=engine,
        )
        data_paths.pop(CUSTOMERS_TABLE_NAME)
        _load_table_to_db(
            path=data_paths[ORDERS_TABLE_NAME], name=ORDERS_TABLE_NAME, engine=engine
        )
        data_paths.pop(ORDERS_TABLE_NAME)

        for table_name, path in data_paths.items():
            df = pd.read_parquet(path)
            df.to_sql(name=table_name, con=engine, index=False)

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
