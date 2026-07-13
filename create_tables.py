import os
from pydantic import BaseModel
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Float,
    Boolean,
)

from dags.schemas.customers import EnrichedCustomersSchema
from dags.schemas.orders import OrdersSchema
from dags.schemas.region_mapping import RegionMappingSchema

PYDANTIC_TO_SQLALCHEMY = {
    str: String,
    int: Integer,
    float: Float,
    bool: Boolean,
}


def create_table_from_pydantic(
    model: type[BaseModel],
    table_name: str,
    metadata: MetaData,
):
    """
    Create a SQLAlchemy table definition from a Pydantic model.
    """

    columns = []

    for field_name, field_info in model.model_fields.items():
        annotation = field_info.annotation

        sqlalchemy_type = PYDANTIC_TO_SQLALCHEMY.get(annotation, String)

        extra = field_info.json_schema_extra or {}
        column_args = []

        column_kwargs = {
            "nullable": extra.get("nullable", True),
        }

        if extra.get("primary_key", False):
            column_kwargs["primary_key"] = True

        columns.append(
            Column(field_name, sqlalchemy_type, *column_args, **column_kwargs)
        )

    return Table(
        table_name,
        metadata,
        *columns,
    )


if __name__ == "__main__":
    engine = create_engine(os.environ.get("DATABASE_URL"))

    metadata = MetaData()

    schemas = {
        "customers": EnrichedCustomersSchema,
        "orders": OrdersSchema,
        "region_mapping": RegionMappingSchema,
    }
    for table_name, schema in schemas.items():
        create_table_from_pydantic(
            model=schema,
            table_name=table_name,
            metadata=metadata,
        )

    metadata.create_all(engine)
    print("Database tables created")
