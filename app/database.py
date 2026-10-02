from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

connect_args={}

if "sqlite" in settings.DATABASE_URL:
    connect_args["check_same_thread"]=False

engine=create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

SessionLocal=async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db()->AsyncGenerator[AsyncSession,None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db()->None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)