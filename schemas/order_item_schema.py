from pydantic import BaseModel

class OrderItemSchema(BaseModel):
    quantity: int
    flavor: str
    size: str
    unit_price: float

    class Config:
        from_attributes = True