import great_expectations as gx
from .base_expectations import build_suite

RAW_CUSTOMERS_SCHEMA = {
    "CustomerID": "object",
    "CompanyName": "object",
    "ContactName": "object",
    "ContactTitle": "object",
    "Address": "object",
    "City": "object",
    "Region": "object",
    "PostalCode": "object",
    "Country": "object",
    "Phone": "object",
    "Fax": "object",
}

ENRICHED_CUSTOMERS_SCHEMA = {
    "CustomerID": "object",
    "CompanyName": "object",
    "ContactName": "object",
    "ContactTitle": "object",
    "Address": "object",
    "City": "object",
    "Region": "object",
    "PostalCode": "object",
    "Country": "object",
    "Phone": "object",
    "Fax": "object",
    "temperature": "float64",
    "humidity": "float64",
    "weather_description": "object",
    "wind_speed": "float64",
    "timestamp": "datetime64[ns]",
    "Region starting 2016": "object",
    "Region until 2017": "object",
}

KEY_COLUMNS = ["CustomerID", "City"]
PRIMARY_KEY_COLUMNS = ["CustomerID"]


def build_first_customers_suite() -> gx.ExpectationSuite:
    return build_suite(
        RAW_CUSTOMERS_SCHEMA,
        KEY_COLUMNS,
        PRIMARY_KEY_COLUMNS,
        name="first_customers_suite",
    )


def build_enriched_customers_suite() -> gx.ExpectationSuite:
    suite = build_suite(
        ENRICHED_CUSTOMERS_SCHEMA,
        KEY_COLUMNS,
        PRIMARY_KEY_COLUMNS,
        name="enriched_customers_suite",
    )
    # Additional expectations for enriched customers
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="temperature")
    )  # Check that OpenWeatherMap API returned temperature data, if null, there is something wrong with the city name
    return suite
