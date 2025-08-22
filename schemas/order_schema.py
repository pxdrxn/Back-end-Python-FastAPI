from pydantic import BaseModel
from typing import List
from schemas.order_item_schema import OrderItemSchema

class OrderSchema(BaseModel):
    user: int       

    class Config:
        from_attributes = True

class ResponseOrderSchema(BaseModel):
    id: int
    status: str
    price: float
    items: List[OrderItemSchema]

    class Config:
        from_attributes = True