from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, Session

from app.backend.db_depends import get_db
from app.models.Order import Order
from app.models.OrderItem import OrderItem
from app.models.OrderStatusEnum import OrderStatusEnum
from app.models.Product import Product
from app.schemas import CreateOrder, CreateOrderItem, OrderStatus

# Создаем маршрутизатор для работы с заказами
router = APIRouter(prefix='/orders',tags=['orders'])

# Эндпоинт для создания заказа
@router.post("/orders", response_model=CreateOrder)
async def create_order(order_data: CreateOrder, db: AsyncSession = Depends(get_db)):
    # Создание заказа с использованием значения перечисления
    db_order = Order(status=order_data.status.value)
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    # Создание элементов заказа и обновление количества на складе
    for item in order_data.items:
        # Получение товара из базы данных
        product = await db.get(Product, item.product_id)

        if product is None:
            raise HTTPException(status_code=404, detail=f"Продукт с идентификатором {item.product_id} не найден")

        # Проверка, хватает ли товара на складе
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Недостаточное количество товара {product.name}. Только {product.stock} единиц.")

        # Создание элемента заказа
        order_item = OrderItem(order_id=db_order.id, product_id=item.product_id, quantity=item.quantity)
        db.add(order_item)

        # Обновление количества на складе
        product.stock -= item.quantity

    await db.commit()
    await db.refresh(db_order)

    # Возвращаем созданный заказ с элементами
    return CreateOrder(
        id=db_order.id,
        created_at=db_order.created_at,
        status=db_order.status,
        items=order_data.items
    )

# Эндпоинт для получения всех заказов
@router.get("/orders", response_model=list[CreateOrder])
async def list_orders(db: AsyncSession = Depends(get_db)):
    # Выполняем жадную загрузку связанных объектов
    result = await db.execute(select(Order).options(selectinload(Order.order_items)))
    orders = result.scalars().all()

    response = []
    for order in orders:
        items = [
            CreateOrderItem(product_id=item.product_id, quantity=item.quantity)
            for item in order.order_items  # Доступ к элементам без ленивой загрузки
        ]
        response.append(CreateOrder(
            id=order.id,
            created_at=order.created_at.isoformat(),
            status=order.status,
            items=items
        ))

    return response

# Эндпоинт для получения заказа по ID
@router.get("/orders/{id}", response_model=CreateOrder)
async def get_order(id: int, db: AsyncSession = Depends(get_db)):
    # Выполняем запрос заказа
    result = await db.execute(select(Order).filter(Order.id == id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Выполняем запрос элементов заказа
    items_result = await db.execute(select(OrderItem).filter(OrderItem.order_id == id))
    order_items = items_result.scalars().all()

    # Формируем список элементов заказа для возврата
    items = [CreateOrderItem(product_id=item.product_id, quantity=item.quantity) for item in order_items]

    # Возвращаем собранные данные в формате модели CreateOrder
    return CreateOrder(
        id=order.id,
        created_at=order.created_at,
        status=order.status,  # Вернем статус как Enum
        items=items  # Возвращаем собранный список элементов заказа
    )

# Эндпоинт для обновления статуса заказа
@router.patch("/orders/{id}/status", response_model=CreateOrder)
async def update_order_status(id: int, status: str, db: AsyncSession = Depends(get_db)):
    # Получаем заказ по ID
    result = await db.execute(select(Order).filter(Order.id == id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    # Обновляем статус заказа
    order.status = status
    await db.commit()
    await db.refresh(order)

    # Получаем элементы заказа
    items_result = await db.execute(select(OrderItem).filter(OrderItem.order_id == id))
    order_items = items_result.scalars().all()

    # Формируем список элементов заказа для возврата
    items = [CreateOrderItem(product_id=item.product_id, quantity=item.quantity) for item in order_items]

    # Возвращаем собранные данные в формате модели CreateOrder
    return CreateOrder(
        id=order.id,
        created_at=order.created_at,
        status=order.status,  # Вернем обновленный статус как Enum
        items=items  # Возвращаем список элементов заказа
    )
