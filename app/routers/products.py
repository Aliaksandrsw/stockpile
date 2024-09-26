from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.backend.db_depends import get_db
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.models.OrderStatusEnum import OrderStatusEnum
from app.models.Product import Product  # Модель SQLAlchemy
from app.schemas import CreateProduct

# Создаем маршрутизатор для работы с товарами
router = APIRouter(prefix='/products', tags=['products'])


# Эндпоинт для создания товара
@router.post("/create_product", response_model=CreateProduct)
async def create_product(product: CreateProduct, db: AsyncSession = Depends(get_db)):
    db_product = Product(**product.dict())  # Преобразуем данные из схемы в модель
    db.add(db_product)  # Добавляем товар в базу данных
    await db.commit()  # Сохраняем изменения
    await db.refresh(db_product)  # Обновляем данные после сохранения
    return db_product  # Возвращаем созданный товар


# Эндпоинт для получения списка всех товаров
@router.get("/all_products", response_model=list[CreateProduct])
async def list_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))  # Получаем все товары из базы данных
    return result.scalars().all()  # Возвращаем список товаров


# Эндпоинт для получения товара по ID
@router.get("/get_product/{id}", response_model=CreateProduct)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == id))  # Ищем товар по ID
    product = result.scalar_one_or_none()  # Получаем один товар или None
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")  # Если товара нет, возвращаем ошибку
    return product  # Возвращаем товар


@router.put("/update_product/{id}", response_model=CreateProduct)
async def update_product(id: int, product_update: CreateProduct, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли товар в заказах
    order_item_exists = await db.execute(
        select(OrderItem).filter(OrderItem.product_id == id)
    )
    if order_item_exists.scalars().first():
        raise HTTPException(status_code=400, detail="Невозможно обновить продукт, он уже находится в заказе")

    # Ищем товар по ID
    result = await db.execute(select(Product).filter(Product.id == id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    # Обновляем поля товара
    for key, value in product_update.dict().items():
        setattr(product, key, value)

    await db.commit()  # Сохраняем изменения
    await db.refresh(product)  # Обновляем данные

    return product  # Возвращаем обновленный товар


# Эндпоинт для удаления товара
@router.delete("/delete_product/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    # Получаем все связанные OrderItem для продукта
    related_orders = await db.execute(
        select(OrderItem).filter(OrderItem.product_id == id)
    )
    order_items = related_orders.scalars().all()

    # Если есть связанные заказы, возвращаем ошибку
    if order_items:
        raise HTTPException(
            status_code=400,
            detail="Невозможно удалить продукт, так как он связан с заказами"
        )

    # Удаляем продукт, если нет связанных заказов
    product = await db.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    await db.delete(product)
    await db.commit()

    return {"message": "Продукт успешно удален"}