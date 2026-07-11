import great_expectations as gx
from .base_expectations import build_suite


CUSTOMERS_SCHEMA = {
    "CustomerID": 'object',
    'CompanyName': 'object',
    'ContactName': 'object',
    'ContactTitle': 'object',
    'Address': 'object',
    'City': 'object',
    'Region': 'object',
    'PostalCode': 'object',
    'Country': 'object',
    'Phone': 'object',
    'Fax': 'object'
}

KEY_COLUMNS = ["CustomerID", "City"]
PRIMARY_KEY_COLUMNS = ["CustomerID"]


def build_first_customers_suite() -> gx.ExpectationSuite:
    return build_suite(CUSTOMERS_SCHEMA, KEY_COLUMNS, PRIMARY_KEY_COLUMNS)