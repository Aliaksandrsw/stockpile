from sqlalchemy import Column, Integer, String, Float
from app.backend.database import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)  # ID товара
    name = Column(String, index=True)  # Название товара
    description = Column(String)  # Описание товара
    price = Column(Float)  # Цена товара
    stock = Column(Integer)  # Количество на складе