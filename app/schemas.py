from datetime import datetime

from pydantic import BaseModel
from enum import Enum
from typing import List


# Перечисление статусов заказа (в Pydantic)
class OrderStatus(str, Enum):
    in_process = "in_process"
    sent = "sent"
    delivered = "delivered"


# Общая модель для товаров (используется для создания и ответа)
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int


# Модель для создания и ответа товара
class CreateProduct(ProductBase):
    id: int = None  # ID товара не требуется при создании, но нужен для ответа

    class Config:
        from_attributes = True  # Позволяет преобразовывать объекты SQLAlchemy в Pydantic-схемы


# Модель для элемента заказа
class CreateOrderItem(BaseModel):
    product_id: int  # ID товара
    quantity: int  # Количество товара


# Модель для создания и ответа на заказ
class CreateOrder(BaseModel):
    id: int = None  # ID заказа (нужно только при ответе)
    created_at: datetime
    status: OrderStatus = OrderStatus.in_process  # Статус заказа, по умолчанию "в процессе"
    items: List[CreateOrderItem]  # Список товаров в заказе

    class Config:
        orm_mode = True


