import great_expectations as gx
from .base_expectations import build_suite
from schemas.region_mapping import RegionMappingSchema

KEY_COLUMNS = ["Country"]
PRIMARY_KEY_COLUMNS = ["Country"]


def build_first_region_mapping_suite() -> gx.ExpectationSuite:
    return build_suite(
        schema=RegionMappingSchema,
        key_columns=KEY_COLUMNS,
        primary_key_columns=PRIMARY_KEY_COLUMNS,
        name="first_region_mapping_suite",
    )
