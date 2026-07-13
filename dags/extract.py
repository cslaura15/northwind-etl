import logging
import sqlite3
import pandas as pd
from pathlib import Path

from config import (
    DATA_DIR,
    REGION_MAPPING_FILE_NAME,
    TABLE_SCHEMA_MAPPING,
)
from utils import normalize_column_names, fetch_weather_data

logger = logging.getLogger(__name__)

def get_sqlite_table(table_name: str, conn: sqlite3.Connection) -> pd.DataFrame:
    """Gets a given table from the SQLite db.

    Args:
        table_name (str): the name of the table that needs to be read
        conn (sqlite3.Connection): the connection to the SQLite db
    
    Returns:
        pd.DataFrame: the content of the table in a DataFrame
    """
    schema = TABLE_SCHEMA_MAPPING[table_name]
    columns = ", ".join(
        f'"{column_name}"' for column_name in schema.model_fields.keys()
    )
    df = pd.read_sql(
        f"""
        SELECT {columns}
        FROM {table_name.title()}
        """,
        conn,
    )
    return df

def get_region_mapping() -> pd.DataFrame:
    """Reads in the region_mapping .xlsx file stored in /data.

    Returns:
        pd.DataFrame: the content of the .xlsx in a DataFrame
    """
    region_mapping_df = pd.read_excel(f"{DATA_DIR}/{REGION_MAPPING_FILE_NAME}")
    region_mapping_df = normalize_column_names(df=region_mapping_df)
    return region_mapping_df


def get_weather_data(cities: list) -> Path:
    """Get weather data for a list of cities.

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