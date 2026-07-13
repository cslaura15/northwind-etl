import great_expectations as gx
from schemas.region_mapping import RegionMappingSchema

from .base_expectations import build_suite


def build_first_region_mapping_suite() -> gx.ExpectationSuite:
    return build_suite(schema=RegionMappingSchema, name="first_region_mapping_suite")
