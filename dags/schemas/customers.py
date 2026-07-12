from datetime import datetime
from pydantic import BaseModel


class RawCustomersSchema(BaseModel):
    CustomerID: str
    CompanyName: str
    ContactName: str
    ContactTitle: str
    Address: str
    City: str
    Region: str
    PostalCode: str
    Country: str
    Phone: str
    Fax: str


class EnrichedCustomersSchema(BaseModel):
    CustomerID: str
    CompanyName: str
    ContactName: str
    ContactTitle: str
    Address: str
    City: str
    Region: str
    PostalCode: str
    Country: str
    Phone: str
    Fax: str
    temperature: float
    humidity: float
    weather_description: str
    wind_speed: float
    timestamp: datetime
    Region_starting_2016: str
    Region_until_2017: str