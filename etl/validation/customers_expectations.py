import great_expectations as gx
from schemas.customers import EnrichedCustomersSchema, RawCustomersSchema

from .base_expectations import build_suite


def build_first_customers_suite() -> gx.ExpectationSuite:
    return build_suite(
        schema=RawCustomersSchema,
        name="first_customers_suite",
    )


def build_enriched_customers_suite() -> gx.ExpectationSuite:
    suite = build_suite(
        schema=EnrichedCustomersSchema,
        name="enriched_customers_suite",
    )
    # Additional expectations for enriched customers
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="temperature")
    )  # Check that OpenWeatherMap API returned temperature data, if null, there is something wrong with the city name
    return suite
