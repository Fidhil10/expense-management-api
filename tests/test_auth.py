import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client:AsyncClient):
    payload={
        "username":"newuser",
        "email":"newuser@example.com",
        "password":"Password123!",
    }

    response=await client.post("/auth/register",json=payload)

    assert response.status_code==201

    data=response.json()

    assert data["username"]=="newuser"
    assert data["email"]=="newuser@example.com"
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username(client:AsyncClient):
    payload={
        "username":"dupuser",
        "email":"dup1@example.com",
        "password":"Password123!",
    }

    res1=await client.post("/auth/register",json=payload)
    assert res1.status_code==201

    payload2={
        "username":"dupuser",
        "email":"dup2@example.com",
        "password":"Password123!",
    }

    res2=await client.post("/auth/register",json=payload2)

    assert res2.status_code==400
    assert "username already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client:AsyncClient):
    payload1={
        "username":"userone",
        "email":"sameemail@example.com",
        "password":"Password123!",
    }

    res1=await client.post("/auth/register",json=payload1)
    assert res1.status_code==201

    payload2={
        "username":"usertwo",
        "email":"sameemail@example.com",
        "password":"Password123!",
    }

    res2=await client.post("/auth/register",json=payload2)

    assert res2.status_code==400
    assert "email already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_oauth2_token_login_success(client:AsyncClient):
    await client.post(
        "/auth/register",
        json={
            "username":"tokenuser",
            "email":"token@example.com",
            "password":"SecretPassword123",
        },
    )

    response=await client.post(
        "/auth/token",
        data={
            "username":"tokenuser",
            "password":"SecretPassword123",
        },
    )

    assert response.status_code==200

    data=response.json()

    assert "access_token" in data
    assert data["token_type"]=="bearer"


@pytest.mark.asyncio
async def test_json_login_success(client:AsyncClient):
    await client.post(
        "/auth/register",
        json={
            "username":"jsonuser",
            "email":"json@example.com",
            "password":"SecretPassword123",
        },
    )

    response=await client.post(
        "/auth/login",
        json={
            "username":"jsonuser",
            "password":"SecretPassword123",
        },
    )

    assert response.status_code==200

    data=response.json()

    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client:AsyncClient):
    await client.post(
        "/auth/register",
        json={
            "username":"failuser",
            "email":"fail@example.com",
            "password":"RightPassword123",
        },
    )

    response=await client.post(
        "/auth/login",
        json={
            "username":"failuser",
            "password":"WrongPassword!",
        },
    )

    assert response.status_code==401
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_profile(
    client:AsyncClient,
    auth_user:dict,
):
    response=await client.get(
        "/auth/me",
        headers=auth_user["headers"],
    )

    assert response.status_code==200

    data=response.json()

    assert data["username"]==auth_user["username"]
    assert data["email"]==auth_user["email"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client:AsyncClient):
    response=await client.get("/auth/me")

    assert response.status_code==401