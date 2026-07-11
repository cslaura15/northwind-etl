import great_expectations as gx
from .base_expectations import build_suite

ORDERS_SCHEMA = {
    "OrderID": 'int64',
    'CustomerID': 'object',
    'EmployeeID': 'int64',
    'OrderDate': 'object',
    'RequiredDate': 'object',
    'ShippedDate': 'object',
    'ShipVia': 'int64',
    'Freight': 'float64',
    'ShipName': 'object',
    'ShipAddress': 'object',
    'ShipCity': 'object',
    'ShipRegion': 'object',
    'ShipPostalCode': 'object',
    'ShipCountry': 'object'
}

KEY_COLUMNS = ["OrderID", "CustomerID"]
PRIMARY_KEY_COLUMNS = ["OrderID"]


def build_first_orders_suite() -> gx.ExpectationSuite:
    return build_suite(ORDERS_SCHEMA, KEY_COLUMNS, PRIMARY_KEY_COLUMNS)
