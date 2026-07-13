import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import great_expectations as gx
import pandas as pd
import requests
from pydantic import BaseModel

from config import DATA_DIR, LOGS_DIR, OPENWEATHER_API_KEY

logger = logging.getLogger(__name__)


def write_to_parquet(df: pd.DataFrame, table_name: str, run_id: str, task: str) -> Path:
    """Writes the given DataFrame to an intermediate parquet file stored in the data/ folder.
    Uses the task and table name and the run id to create a unique file name.

    Args:
        df (pd.DataFrame): the DataFrame that should be written to the parquet file
        table_name (str): name of the table stored in the DataFrame
        run_id (str): the unique run_id of the Airflow run
        task (str): the name of the task that runs this function

    Returns:
        Path: _description_
    """
    data_path = f"{DATA_DIR}/{task}_{table_name}_{run_id}.parquet"
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
    """Write the full validation result as JSON to logs/validation/.

    Args:
        result (gx.core.ExpectationSuiteValidationResult): the validation result
        log_file_name (str): file name (like extract_customers)
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


def get_primary_keys(schema: type[BaseModel]) -> list[str]:
    """Gets all the primary keys from the given Pydantic schema model.

    Args:
        schema (type[BaseModel]): the Pydantic model

    Returns:
        list[str]: list of the names of the primary key columns
    """
    return [
        name
        for name, field in schema.model_fields.items()
        if field.json_schema_extra.get("primary_key", False)
    ]
