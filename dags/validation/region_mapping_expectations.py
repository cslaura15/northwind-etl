import great_expectations as gx
from .base_expectations import build_suite


REGION_MAPPING_SCHEMA = {
    'Country': 'object',
    'Region starting 2016': 'object',
    'Region until 2017': 'object'
}

KEY_COLUMNS = ["Country"]
PRIMARY_KEY_COLUMNS = ["Country"]


def build_first_region_mapping_suite() -> gx.ExpectationSuite:
    return build_suite(REGION_MAPPING_SCHEMA, KEY_COLUMNS, PRIMARY_KEY_COLUMNS, name="first_region_mapping_suite")