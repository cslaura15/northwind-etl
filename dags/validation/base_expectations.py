import great_expectations as gx
import pandas as pd


def build_suite(schema: dict, key_columns: list, primary_key_columns: list, name: str) -> gx.ExpectationSuite:
    suite = gx.ExpectationSuite(name=name)

    # SCHEMA EXPECTATIONS
    suite.add_expectation(
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=list(schema.keys()),
            exact_match=True
        )
    )

    # DATA TYPE EXPECTATIONS
    for column, dtype in schema.items():
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeOfType(
                column=column,
                type_=dtype
            )
        )

    # NULL VALUE EXPECTATIONS
    for column in key_columns:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column=column)
        )
    
    # UNIQUENESS EXPECTATIONS
    if len(primary_key_columns) == 1:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeUnique(column=primary_key_columns[0])
        )
    else:
        suite.add_expectation(
            gx.expectations.ExpectCompoundColumnsToBeUnique(column_list=primary_key_columns)
        )

    return suite