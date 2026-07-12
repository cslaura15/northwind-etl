from pydantic import BaseModel    


class OrdersSchema(BaseModel):
    OrderID: int
    CustomerID: str
    EmployeeID: int
    OrderDate: str
    RequiredDate: str
    ShippedDate: str
    ShipVia: int
    Freight: float
    ShipName: str
    ShipAddress: str
    ShipCity: str
    ShipRegion: str
    ShipPostalCode: str
    ShipCountry: str