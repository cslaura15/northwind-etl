import json
import logging
import os
import requests
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import great_expectations as gx
import pandas as pd

from schemas.customers import RawCustomersSchema
from schemas.orders import OrdersSchema
from config import (
    DATA_DIR,
    CUSTOMERS_TABLE_NAME,
    LOGS_DIR,
    ORDERS_TABLE_NAME,
    REGION_MAPPING_FILE_NAME
)


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

def write_to_parquet(df: pd.DataFrame, table_name: str, run_id: str) -> Path:
    data_path = (
        f"{DATA_DIR}/extract_{table_name}_{run_id}.parquet"
    )
    df.to_parquet(data_path, index=False)
    return data_path


def fetch_weather_data(city: str) -> pd.DataFrame:
    """
    Fetch weather data for a given city using the OpenWeatherMap API.

    Args:
        city (str): The name of the city to fetch weather data for.

    Returns:
        pd.DataFrame: A DataFrame containing the weather data for the specified city.
    """
    request_url = f"http://api.openweathermap.org/data/2.5/weather/?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(request_url)
    if response.status_code == 200:
        data = response.json()
        weather_data = {
            "city": data.get("name"),
            "temperature": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "weather_description": data["weather"][0].get("description"),
            "wind_speed": data["wind"].get("speed"),
            "timestamp": pd.Timestamp.now(),
        }
        return pd.DataFrame([weather_data])
    else:
        raise Exception(
            f"Failed to fetch weather data for {city}. Status code: {response.status_code}, Response: {response.text}"
        )


def save_result(
    result: gx.core.ExpectationSuiteValidationResult, log_file_name: str
) -> None:
    """
    Write the full validation result as JSON to logs/validation/.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = LOGS_DIR / f"{log_file_name}_{timestamp}.json"

    with open(json_path, "w") as f:
        json.dump(result.to_json_dict(), f, indent=2, default=str)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names by replacing spaces with underscores.

    Args:
        df (pd.DataFrame): The DataFrame whose column names should be normalized.

    Returns:
        pd.DataFrame: A new DataFrame with normalized column names.
    """
    new_columns = {
        col: col.replace(" ", "_") if isinstance(col, str) else col
        for col in df.columns
    }
    return df.rename(columns=new_columns)
