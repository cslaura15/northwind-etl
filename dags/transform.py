import pandas as pd


def enrich_customers_with_weather(customers_df: pd.DataFrame, weather_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the customers DataFrame with weather data based on the city.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame.
        weather_data_df (pd.DataFrame): The weather data DataFrame.

    Returns:
        pd.DataFrame: The enriched customers DataFrame with weather information.
    """
    enriched_customers_df = customers_df.merge(
        weather_data_df,
        how="left",
        left_on="City",
        right_on="city"
    )
    return enriched_customers_df

def enrich_customers_with_region(customers_df: pd.DataFrame, region_mapping_df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the customers DataFrame with region data based on the country.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame.
        region_mapping_df (pd.DataFrame): The region mapping DataFrame.

    Returns:
        pd.DataFrame: The enriched customers DataFrame with region information.
    """
    enriched_customers_df = customers_df.merge(
        region_mapping_df,
        how="left",
        left_on="Country",
        right_on="Country"
    )
    return enriched_customers_df