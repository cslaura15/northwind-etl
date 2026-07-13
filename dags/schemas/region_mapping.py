from pydantic import BaseModel, Field


class RegionMappingSchema(BaseModel):
    Country: str = Field(
        json_schema_extra={
            "primary_key": True,
            "foreign_key": False,
            "nullable": False
        }
    )
    Region_starting_2016: str = Field(
        json_schema_extra={
            "primary_key": False,
            "foreign_key": False,
            "nullable": False
        }
    )
    Region_until_2017: str = Field(
        json_schema_extra={
            "primary_key": False,
            "foreign_key": False,
            "nullable": False
        }
    )
