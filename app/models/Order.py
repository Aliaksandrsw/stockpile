from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.backend.database import Base
from app.models.OrderStatusEnum import OrderStatusEnum


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)  # ID заказа
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Время создания
    status = Column(Enum(OrderStatusEnum), default=OrderStatusEnum.in_process)  # Статус заказа
    order_items = relationship("OrderItem", back_populates="order")  # Связь с элементами заказа