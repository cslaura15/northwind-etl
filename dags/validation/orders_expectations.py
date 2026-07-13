import great_expectations as gx
from .base_expectations import build_suite
from schemas.orders import OrdersSchema


def build_first_orders_suite() -> gx.ExpectationSuite:
    return build_suite(schema=OrdersSchema, name="first_orders_suite")
