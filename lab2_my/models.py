import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship

from database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    cooking = "cooking"
    done = "done"


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    dishes = relationship("Dish", back_populates="category", cascade="all, delete-orphan")


class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="dishes")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    quantity = Column(Integer, default=1)
    status = Column(Enum(OrderStatus, name="order_status"), default=OrderStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    dish = relationship("Dish")