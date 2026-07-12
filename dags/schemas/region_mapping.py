from pydantic import BaseModel


class RegionMappingSchema(BaseModel):
    Country: str
    Region_starting_2016: str
    Region_until_2017: str
