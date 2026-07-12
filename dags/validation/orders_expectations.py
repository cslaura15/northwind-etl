import great_expectations as gx
from .base_expectations import build_suite
from schemas.orders import OrdersSchema


KEY_COLUMNS = ["OrderID", "CustomerID"]
PRIMARY_KEY_COLUMNS = ["OrderID"]


def build_first_orders_suite() -> gx.ExpectationSuite:
    return build_suite(
        schema=OrdersSchema, key_columns=KEY_COLUMNS, primary_key_columns=PRIMARY_KEY_COLUMNS, name="first_orders_suite"
    )
