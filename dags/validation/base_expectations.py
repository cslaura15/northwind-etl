import great_expectations as gx
from datetime import datetime


TYPE_MAPPING = {
    str: "object",
    int: "int64",
    float: "float64",
    bool: "bool",
    datetime: "datetime64[ns]",
}

def build_suite(schema, name: str) -> gx.ExpectationSuite:
    suite = gx.ExpectationSuite(name=name)

    # SCHEMA EXPECTATIONS
    suite.add_expectation(
        gx.expectations.ExpectTableColumnsToMatchSet(
            column_set=list(schema.model_fields.keys()), exact_match=True
        )
    )

    # DATA TYPE EXPECTATIONS
    num_primary_keys = 0
    primary_key_columns = []
    for column, field_info in schema.model_fields.items():
        extra = field_info.json_schema_extra or {}

        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeOfType(column=column, type_=TYPE_MAPPING[field_info.annotation])
        )

        # NULL VALUE EXPECTATIONS
        if not extra.get("nullable"):
            suite.add_expectation(
                gx.expectations.ExpectColumnValuesToNotBeNull(column=column)
            )

        if extra.get("primary_key"):
            num_primary_keys += 1
            primary_key_columns.append(column)

    # UNIQUENESS EXPECTATIONS
    if num_primary_keys == 1:
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeUnique(column=primary_key_columns[0])
        )
    elif num_primary_keys > 1:
        suite.add_expectation(
            gx.expectations.ExpectCompoundColumnsToBeUnique(
                column_list=primary_key_columns
            )
        )

    return suite
