import json
import os
import requests
from datetime import datetime, timezone
from pathlib import Path

import great_expectations as gx
import pandas as pd

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
LOGS_DIR = Path("logs/validation")
LOGS_DIR.mkdir(exist_ok=True)


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
            "timestamp": pd.Timestamp.now()
        }
        return pd.DataFrame([weather_data])
    else:
        raise Exception(f"Failed to fetch weather data for {city}. Status code: {response.status_code}, Response: {response.text}")


def fetch_all_weather_data(cities: list) -> pd.DataFrame:
    """
    Fetch weather data for a list of cities.

    Args:
        cities (list): A list of city names to fetch weather data for. 

    Returns:
        pd.DataFrame: A DataFrame containing the weather data for all specified cities.
    """
    all_weather_data = pd.DataFrame()
    for city in cities:
        try:
            city_weather_data = fetch_weather_data(city)
            all_weather_data = pd.concat([all_weather_data, city_weather_data], ignore_index=True)
        except Exception as e:
            print(f"Error fetching data for {city}: {e}")
    return all_weather_data


def save_result(result: gx.core.ExpectationSuiteValidationResult) -> None:
    """
    Write the full validation result as JSON to logs/validation/.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = LOGS_DIR / f"validation_{timestamp}.json"
 
    with open(json_path, "w") as f:
        json.dump(result.to_json_dict(), f, indent=2, default=str)
