from pydantic import BaseModel, Field 


class OrdersSchema(BaseModel):
    OrderID: int = Field(
        json_schema_extra={
            "primary_key": True,
            "nullable": False
        }
    )
    CustomerID: str = Field(
        json_schema_extra={
            "primary_key": False,
            "foreign_key": "customers.CustomerID",
            "nullable": False
        }
    )
    EmployeeID: int = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    OrderDate: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    RequiredDate: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShippedDate: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": True
        }
    )
    ShipVia: int = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    Freight: float = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipName: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipAddress: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipCity: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipRegion: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipPostalCode: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )
    ShipCountry: str = Field(
        json_schema_extra={
            "primary_key": False,
            "nullable": False
        }
    )