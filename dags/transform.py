import logging

import great_expectations as gx
import pandas as pd

from expectations.customers_expectations import build_first_customers_suite
from expectations.orders_expectations import build_first_orders_suite
from expectations.region_mapping_expectations import build_first_region_mapping_suite
from utils import save_result

logger = logging.getLogger(__name__)

def run_first_validations(
    customers_df: pd.DataFrame = None, 
    orders_df: pd.DataFrame = None, 
    region_mapping_df: pd.DataFrame = None, 
):
    table_function_mapping = {
        'customers': {
            'df': customers_df,
            'suite_func': build_first_customers_suite
        },
        'orders': {
            'df': orders_df,
            'suite_func': build_first_orders_suite
        },
        'region_mapping': {
            'df': region_mapping_df,
            'suite_func': build_first_region_mapping_suite
        }
    }
    for table_name, info in table_function_mapping.items():
        df = info['df']
        build_suite_func = info['suite_func']
        logger.info(f"Validating table {table_name} with func {build_suite_func}")
        if build_suite_func:
            result = validate_df(df, table_name, build_suite_func)
        
        if not result.success:
            logger.error(f"Validation failed for table {table_name}. See logs for details.")
            save_result(result=result)
        else:
            logger.info(f"Validation passed for table {table_name}.")
        
def validate_df(df: pd.DataFrame, table_name: str, build_suite_func) -> gx.core.ExpectationSuiteValidationResult:
        context = gx.get_context(mode="ephemeral")
 
        data_source = context.data_sources.add_pandas("pandas_source")
        data_asset = data_source.add_dataframe_asset(name=f"{table_name}_asset")
        batch_definition = data_asset.add_batch_definition_whole_dataframe(
            f"batch_definition_{table_name}"
        )
    
        suite = context.suites.add(build_suite_func())
    
        validation_definition = context.validation_definitions.add(
            gx.ValidationDefinition(
                name=f"validation_definition_{table_name}",
                data=batch_definition,
                suite=suite,
            )
        )
    
        result = validation_definition.run(batch_parameters={"dataframe": df})
        return result

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