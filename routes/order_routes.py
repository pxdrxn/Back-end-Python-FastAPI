from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import catch_session, verify_token
from models.models import Order, User, OrderItem
from schemas.order_item_schema import OrderItemSchema
from schemas.order_schema import OrderSchema, ResponseOrderSchema

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(verify_token)]
)

@order_router.get("/")
async def order():
    return {"message": "You accessed the orders endpoint"}

@order_router.post("/order")
async def create_order(
    order_schema: OrderSchema,
    session: Session = Depends(catch_session)
):
    new_order = Order(user=order_schema.user)
    session.add(new_order)
    session.commit()
    return {"message": f"Order created successfully order_id: {new_order.id}"}

@order_router.get("/list")
async def list_all_orders(
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    if user.admin == False:
        raise HTTPException(status_code=401, detail="You do not have permission to list orders")
    else:
        orders = session.query(Order).all()
        return {"Orders": orders}

@order_router.get("/list/user_order", response_model=List[ResponseOrderSchema])
async def list_orders(
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    orders = session.query(Order).filter(Order.user == user.id).all()
    return orders

@order_router.get("/order/{order_id}")
async def view_order(
    order_id: int,
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=401, detail="You do not have permission to view this order")
    return {
        "quantity_order_items": len(order.items),
        "order": order
    }

@order_router.patch("/order/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    allowed_statuses = ["IN_PROGRESS", "CANCELLED", "COMPLETED"]
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed_statuses}")

    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")

    if not user.admin:
        raise HTTPException(status_code=401, detail="You do not have permission to update this order")

    order.status = status
    session.commit()

    return {
        "message": f"Order number {order.id} status updated to {status} successfully",
        "order": order
    }

@order_router.post("/order/add-item/{order_id}")
async def add_order_item(
    order_id: int,
    order_item_schema: OrderItemSchema,
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not existing")

    if order.status in ["IN_PROGRESS", "COMPLETED", "CANCELLED"]:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot add items when the order status is {order.status}"
        )

    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=401, detail="You do not have permission to add item for order.")
        
    order_item = OrderItem(
        order_item_schema.quantity,
        order_item_schema.flavor,
        order_item_schema.size,
        order_item_schema.unit_price,
        order_id
    )
    session.add(order_item)
    order.calc_price()
    session.commit()
    return {
        "message": "Item created successfully",
        "item_id": order_item.id,
        "price_order": order.price
    }

@order_router.delete("/order/remove-item/{order_item_id}")
async def remove_order_item(
    order_item_id: int,
    session: Session = Depends(catch_session),
    user: User = Depends(verify_token)
):
    order_item = session.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    order = session.query(Order).filter(Order.id == order_item.order).first()
    if not order_item:
        raise HTTPException(status_code=400, detail="Item in order not existing")

    if order.status in ["IN_PROGRESS", "COMPLETED", "CANCELLED"]:
        raise HTTPException(
            status_code=400,
            detail=f"You cannot remove items when the order status is {order.status}"
        )

    if not user.admin and user.id != order.user:
        raise HTTPException(status_code=401, detail="You do not have permission to add item for order.")
        
    session.delete(order_item)
    order.calc_price()
    session.commit()
    return {
        "message": "Item removed successfully",
        "quantity_order_items": len(order.items),
        "price_order": order.price
    }