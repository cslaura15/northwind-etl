import logging
from types import FunctionType

import great_expectations as gx
import pandas as pd
from pydantic import BaseModel
from utils import save_result, write_to_parquet
from validation.customers_expectations import (build_enriched_customers_suite,
                                               build_first_customers_suite)
from validation.orders_expectations import build_first_orders_suite
from validation.region_mapping_expectations import \
    build_first_region_mapping_suite

from config import TABLE_SCHEMA_MAPPING

logger = logging.getLogger(__name__)


def run_first_validations(
    customers_df: pd.DataFrame = None,
    orders_df: pd.DataFrame = None,
    region_mapping_df: pd.DataFrame = None,
):
    """Runs the validations on the DataFrames for the first time.
    Builds the Great Expectation suites for all the tables, runs them and saves the result if the validation failed.

    Args:
        customers_df (pd.DataFrame, optional): the customers table in DataFrame
        orders_df (pd.DataFrame, optional): the orders table in DataFrame
        region_mapping_df (pd.DataFrame, optional): the region_mapping table in DataFrame
    """
    table_function_mapping = {
        "customers": {"df": customers_df, "suite_func": build_first_customers_suite},
        "orders": {"df": orders_df, "suite_func": build_first_orders_suite},
        "region_mapping": {
            "df": region_mapping_df,
            "suite_func": build_first_region_mapping_suite,
        },
    }
    for table_name, info in table_function_mapping.items():
        logger.info(f"Running first validation on {table_name} ...")
        df = info["df"]
        build_suite_func = info["suite_func"]
        if build_suite_func:
            result = validate_df(df, table_name, build_suite_func)

        if not result.success:
            logger.error(
                f"Validation failed for table {table_name}. See logs for details."
            )
            save_result(result=result, log_file_name=f"validation_{table_name}")
        else:
            logger.info(f"Validation passed for table {table_name}.")


def run_second_validations(enriched_customers_df: pd.DataFrame = None):
    """Runs the second round of validations on the given DataFrames.
    Builds the Great Expectation suites for all the tables, runs them and saves the result if the validation failed.

    Args:
        enriched_customers_df (pd.DataFrame, optional): the enriched customers table in DataFrame
    """
    table_name = "enriched_customers"
    logger.info(f"Running second validation on {table_name} ...")
    result = validate_df(
        enriched_customers_df, table_name, build_enriched_customers_suite
    )
    if not result.success:
        logger.error(f"Validation failed for table {table_name}. See logs for details.")
        save_result(result=result, log_file_name=f"validation_{table_name}")
    else:
        logger.info(f"Validation passed for table {table_name}.")


def validate_df(
    df: pd.DataFrame, table_name: str, build_suite_func: FunctionType
) -> gx.core.ExpectationSuiteValidationResult:
    """Validates one DataFrame based on the given build_suite_func.

    Args:
        df (pd.DataFrame): the given DataFrame
        table_name (str): the table name used for Great Expectation namings
        build_suite_func (FunctionType): the unique function that builds the validation suite for the table

    Returns:
        gx.core.ExpectationSuiteValidationResult: the validation result
    """
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


def enrich_customers(
    customers_df: pd.DataFrame,
    weather_data_df: pd.DataFrame,
    region_mapping_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enrich the customers DataFrame with weather and region data.

    Args:
        customers_df (pd.DataFrame): The customers DataFrame.
        weather_data_df (pd.DataFrame): The weather data DataFrame.
        region_mapping_df (pd.DataFrame): The region mapping DataFrame.

    Returns:
        pd.DataFrame: The enriched customers DataFrame with weather and region information.
    """
    logger.info(f"Running customers enrichment ...")
    weather_data_df = weather_data_df.rename(columns={"city": "City"})
    enriched_customers_df = customers_df.merge(
        weather_data_df, how="left", on="City"
    ).merge(region_mapping_df, how="left", on="Country")
    logger.info(f"Number of rows before and after enrichment: {len(customers_df)} and {len(enriched_customers_df)}")
    return enriched_customers_df


def split_valid_quarantine(
    df: pd.DataFrame,
    schema: type[BaseModel],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits the given DataFrame to valid and quarantined dfs based on the given Pydantic model.
    If a row violates any of the constraints, it is moved to the quarantine df.

    Args:
        df (pd.DataFrame): the given DataFrame to run the splitting on
        schema (type[BaseModel]): the table schema with constraints

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: the valid and quarantined DataFrames
    """

    invalid_mask = pd.Series(False, index=df.index)
    reasons = pd.Series("", index=df.index, dtype="object")

    def add_reason(mask: pd.Series, reason: str):
        nonlocal invalid_mask, reasons

        invalid_mask |= mask
        reasons.loc[mask] = reasons.loc[mask].apply(
            lambda r: reason if r == "" else f"{r}; {reason}"
        )

    # Nullability checks
    for column, field_info in schema.model_fields.items():
        extra = field_info.json_schema_extra or {}

        if not extra.get("nullable", True):
            mask = df[column].isna()
            add_reason(mask, f"{column} is NULL")

    # Primary key duplicate checks
    primary_keys = [
        column
        for column, field_info in schema.model_fields.items()
        if (field_info.json_schema_extra or {}).get("primary_key")
    ]

    if primary_keys:
        duplicate_mask = df.duplicated(
            subset=primary_keys,
            keep=False,
        )
        add_reason(duplicate_mask, f"Duplicate primary key ({', '.join(primary_keys)})")

    quarantine_df = df[invalid_mask].copy()
    quarantine_df["quarantine_reason"] = reasons[invalid_mask]

    valid_df = df[~invalid_mask].copy()

    return valid_df, quarantine_df


def clean_and_quarantine(df: pd.DataFrame, table_name: str, run_id: str):
    """Split a dataframe into valid/quarantine rows and persist quarantine to parquet.

    Args:
        df (pd.DataFrame): the DataFrame that should be cleaned
        table_name (str): name of the table
        run_id (str): the unique run id of the Airflow run (to generate unique file names)

    Returns:
        _type_: the path to the valid and quarantined parquet files
    """
    logger.info(f"Running cleaning on {table_name} ...")
    valid_df, quarantine_df = split_valid_quarantine(
        df=df, schema=TABLE_SCHEMA_MAPPING[table_name]
    )
    quarantine_path = write_to_parquet(
        df=quarantine_df,
        table_name=f"quarantined_{table_name}",
        run_id=run_id,
        task="transform",
    )

    valid_path = write_to_parquet(
        df=valid_df, table_name=f"valid_{table_name}", run_id=run_id, task="transform"
    )
    logger.info(f"Number of valid rows: {len(valid_df)} and invalid rows: {len(quarantine_df)}")
    return valid_path, quarantine_path
