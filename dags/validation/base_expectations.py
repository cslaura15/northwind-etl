import great_expectations as gx
from datetime import datetime


TYPE_MAPPING = {
    str: "object",
    int: "int64",
    float: "float64",
    bool: "bool",
    datetime: "datetime64[ns]",
}

def build_suite(
    schema, key_columns: list, primary_key_columns: list, name: str
) -> gx.ExpectationSuite:
    suite = gx.ExpectationSuite(name=name)

    # SCHEMA EXPECTATIONS
    suite.add_expectation(
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=list(schema.model_fields.keys()), exact_match=True
        )
    )

    # DATA TYPE EXPECTATIONS
    for column, field_info in schema.model_fields.items():
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeOfType(column=column, type_=TYPE_MAPPING[field_info.annotation])
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
            gx.expectations.ExpectCompoundColumnsToBeUnique(
                column_list=primary_key_columns
            )
        )

    return suite
