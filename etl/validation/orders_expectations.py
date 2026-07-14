import great_expectations as gx
from schemas.orders import OrdersSchema

from .base_expectations import build_suite


def build_first_orders_suite() -> gx.ExpectationSuite:
    return build_suite(schema=OrdersSchema, name="first_orders_suite")
