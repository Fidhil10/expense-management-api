from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport,AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine

from app.database import Base,get_db
from app.main import app


TEST_DATABASE_URL="sqlite+aiosqlite:///:memory:"

test_engine=create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread":False},
)

TestSessionLocal=async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db()->AsyncGenerator[AsyncSession,None]:
    async with TestSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db]=override_get_db


@pytest_asyncio.fixture
async def client()->AsyncGenerator[AsyncClient,None]:
    transport=ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_user(client:AsyncClient)->dict:
    user_data={
        "username":"testuser",
        "email":"testuser@example.com",
        "password":"Password123!",
    }

    reg_res=await client.post("/auth/register",json=user_data)
    assert reg_res.status_code==201

    login_res=await client.post(
        "/auth/token",
        data={
            "username":user_data["username"],
            "password":user_data["password"],
        },
    )

    assert login_res.status_code==200

    token=login_res.json()["access_token"]
    headers={"Authorization":f"Bearer {token}"}

    return {
        "username":user_data["username"],
        "email":user_data["email"],
        "token":token,
        "headers":headers,
    }


@pytest_asyncio.fixture
async def second_user(client:AsyncClient)->dict:
    user_data={
        "username":"seconduser",
        "email":"second@example.com",
        "password":"Password456!",
    }

    reg_res=await client.post("/auth/register",json=user_data)
    assert reg_res.status_code==201

    login_res=await client.post(
        "/auth/token",
        data={
            "username":user_data["username"],
            "password":user_data["password"],
        },
    )

    assert login_res.status_code==200

    token=login_res.json()["access_token"]
    headers={"Authorization":f"Bearer {token}"}

    return {
        "username":user_data["username"],
        "email":user_data["email"],
        "token":token,
        "headers":headers,
    }