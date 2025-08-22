from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types import ChoiceType



db = create_engine("sqlite:///banco.db")


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(50))
    email = Column("email", String(50), nullable=False)
    password = Column("password", String(50))
    active = Column("active", Boolean)
    admin = Column("admin", Boolean, default=False)

    def __init__(self, name, email, password, active=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.admin = admin


class Order(Base):
    __tablename__ = "orders"

   # STATUS_ORDERS = (
   #     ("PENDING", "PENDING"),
   #     ("IN_PROGRESS", "IN_PROGRESS"),
   #     ("CANCELLED", "CANCELLED"),
   #     ("COMPLETED", "COMPLETED"),
   # )

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    status = Column("status", String)
    user = Column("user", ForeignKey("users.id"))
    price = Column("price", Float)
    items = relationship("OrderItem", cascade="all, delete")

    def __init__(self, user, status="PENDING", price=0):
        self.user = user
        self.price = price
        self.status = status

    def calc_price(self):

       self.price = sum(item.unit_price * item.quantity for item in self.items)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantity = Column("quantity", Integer)
    flavor = Column("flavor", String(50))
    size = Column("size", String(50))
    unit_price = Column("unit_price", Float)
    order = Column("order", ForeignKey("orders.id"))

    def __init__(self, quantity, flavor, size, unit_price, order):
        self.quantity = quantity
        self.flavor = flavor
        self.size = size
        self.unit_price = unit_price
        self.order = order   