from datetime import datetime
from pydantic import BaseModel, Field


class RawCustomersSchema(BaseModel):
    CustomerID: str = Field(json_schema_extra={"primary_key": True, "nullable": False})
    CompanyName: str = Field(json_schema_extra={"primary_key": False, "nullable": True})
    ContactName: str = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    ContactTitle: str = Field(
        json_schema_extra={"primary_key": False, "nullable": True}
    )
    Address: str = Field(json_schema_extra={"primary_key": False, "nullable": False})
    City: str = Field(json_schema_extra={"primary_key": False, "nullable": False})
    Region: str = Field(json_schema_extra={"primary_key": False, "nullable": True})
    PostalCode: str = Field(json_schema_extra={"primary_key": False, "nullable": False})
    Country: str = Field(json_schema_extra={"primary_key": False, "nullable": False})
    Phone: str = Field(json_schema_extra={"primary_key": False, "nullable": True})
    Fax: str = Field(json_schema_extra={"primary_key": False, "nullable": True})


class EnrichedCustomersSchema(RawCustomersSchema):
    temperature: float = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    humidity: float = Field(json_schema_extra={"primary_key": False, "nullable": False})
    weather_description: str = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    wind_speed: float = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    timestamp: datetime = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    Region_starting_2016: str = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
    Region_until_2017: str = Field(
        json_schema_extra={"primary_key": False, "nullable": False}
    )
