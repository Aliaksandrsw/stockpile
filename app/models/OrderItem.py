from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.backend.database import Base


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)  # ID элемента заказа
    order_id = Column(Integer, ForeignKey('orders.id'))  # Связь с заказом
    product_id = Column(Integer, ForeignKey('products.id'))  # Связь с товаром
    quantity = Column(Integer)  # Количество товара в заказе
    order = relationship("Order", back_populates="order_items")  # Связь с заказом
    product = relationship("Product")  # Связь с товаром
