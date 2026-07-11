import great_expectations as gx



def build_suite(schema: dict, key_columns: list, primary_key_columns: list) -> gx.ExpectationSuite:
    suite = gx.ExpectationSuite(name="first_customers_suite")

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
    suite.add_expectation(
        gx.expectations.ExpectCompoundColumnsToBeUnique(columns=primary_key_columns)
    )

