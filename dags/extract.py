import logging
import sqlite3
import pandas as pd
from pathlib import Path

from schemas.customers import RawCustomersSchema
from schemas.orders import OrdersSchema

from config import (
    DATA_DIR,
    CUSTOMERS_TABLE_NAME,
    ORDERS_TABLE_NAME,
    REGION_MAPPING_FILE_NAME
)
from utils import normalize_column_names, fetch_weather_data

logger = logging.getLogger(__name__)

def get_customers_data(conn: sqlite3.Connection) -> pd.DataFrame:
    customer_columns = ", ".join(
        f'"{column_name}"' for column_name in RawCustomersSchema.model_fields.keys()
    )
    customers_df = pd.read_sql(
        f"""
        SELECT {customer_columns}
        FROM {CUSTOMERS_TABLE_NAME}
        """,
        conn,
    )
    return customers_df

def get_orders_data(conn: sqlite3.Connection) -> pd.DataFrame:
    order_columns = ", ".join(
        f'"{column_name}"' for column_name in OrdersSchema.model_fields.keys()
    )
    orders_df = pd.read_sql(
        f"""
        SELECT {order_columns}
        FROM {ORDERS_TABLE_NAME}
        """,
        conn,
    )
    return orders_df

def get_region_mapping() -> pd.DataFrame:
    region_mapping_df = pd.read_excel(f"{DATA_DIR}/{REGION_MAPPING_FILE_NAME}")
    region_mapping_df = normalize_column_names(df=region_mapping_df)
    return region_mapping_df


def get_weather_data(cities: list) -> Path:
    """
    Get weather data for a list of cities.

    Args:
        cities (list): A list of city names to fetch weather data for.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data for all specified cities.
    """
    all_weather_data = pd.DataFrame()
    for city in cities:
        try:
            city_weather_data = fetch_weather_data(city)
            city_weather_data["city"] = (
                city  # Ensure the city name matches the requested city
            )
            all_weather_data = pd.concat(
                [all_weather_data, city_weather_data], ignore_index=True
            )
        except Exception as e:
            logger.error(f"Error fetching data for {city}: {e}")
    return all_weather_data