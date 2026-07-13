import os
from pathlib import Path

CUSTOMERS_TABLE_NAME = "customers"
DATA_DIR = "/opt/airflow/data"
DEST_DB_PATH = os.environ.get("POSTGRES_DEST_CONN")
LOGS_DIR = Path("logs/validation")
LOGS_DIR.mkdir(exist_ok=True)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
ORDERS_TABLE_NAME = "orders"
REGION_MAPPING_FILE_NAME = "region_mapping_DE.xlsx"
REGION_MAPPING_NAME = "region_mapping"
SOURCE_DB_PATH = os.environ.get("SQLITE_SRC_PATH", "/opt/airflow/data/northwind.db")
WEATHER_DATA_NAME = "weather_data"
