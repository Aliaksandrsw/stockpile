from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

#engine = create_async_engine('postgresql+asyncpg://user_stock:1234@localhost:5432/stock', echo=True)
engine = create_async_engine('postgresql+asyncpg://user_stock:1234@db:5432/stock', echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass
