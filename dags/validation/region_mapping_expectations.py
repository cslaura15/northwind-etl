import great_expectations as gx
from .base_expectations import build_suite
from schemas.region_mapping import RegionMappingSchema


def build_first_region_mapping_suite() -> gx.ExpectationSuite:
    return build_suite(schema=RegionMappingSchema, name="first_region_mapping_suite")
