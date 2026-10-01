"""Tests for salary creation, retrieval, and cumulative/monthly financial totals."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_totals_empty(client: AsyncClient, auth_user: dict):
    """Test totals return zeros when no expenses or salaries are recorded."""
    response = await client.get("/totals/", headers=auth_user["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["total_expense"] == 0.0
    assert data["total_salary"] == 0.0
    assert data["remaining_amount"] == 0.0


@pytest.mark.asyncio
async def test_add_salary_and_calculate_totals(client: AsyncClient, auth_user: dict):
    """Requirement 1.5: Test total expense, total salary, and remaining amount calculation."""
    # 1. Add salary
    salary_payload = {"amount": 5000.0}
    salary_res = await client.post(
        "/salary/",
        json=salary_payload,
        headers=auth_user["headers"],
    )
    assert salary_res.status_code == 201
    assert salary_res.json()["amount"] == 5000.0

    # 2. Add two expenses
    await client.post(
        "/expenses/",
        json={"name": "Rent", "amount": 1200.0, "category": "Housing"},
        headers=auth_user["headers"],
    )
    await client.post(
        "/expenses/",
        json={"name": "Utilities", "amount": 300.0, "category": "Bills"},
        headers=auth_user["headers"],
    )

    # 3. Fetch totals
    totals_res = await client.get("/totals/", headers=auth_user["headers"])
    assert totals_res.status_code == 200
    data = totals_res.json()
    assert data["total_expense"] == 1500.0
    assert data["total_salary"] == 5000.0
    assert data["remaining_amount"] == 3500.0


@pytest.mark.asyncio
async def test_list_salaries(client: AsyncClient, auth_user: dict):
    """Test retrieving salary records."""
    await client.post(
        "/salary/",
        json={"amount": 4500.0},
        headers=auth_user["headers"],
    )
    await client.post(
        "/salary/",
        json={"amount": 500.0},
        headers=auth_user["headers"],
    )

    response = await client.get("/salary/", headers=auth_user["headers"])
    assert response.status_code == 200
    salaries = response.json()
    assert len(salaries) == 2
    assert sum(s["amount"] for s in salaries) == 5000.0


@pytest.mark.asyncio
async def test_monthly_totals(client: AsyncClient, auth_user: dict):
    """Test monthly scoped financial metrics."""
    # Add salary in October
    await client.post(
        "/salary/",
        json={"amount": 4000.0, "created_at": "2026-10-01T09:00:00"},
        headers=auth_user["headers"],
    )
    # Add expense in October
    await client.post(
        "/expenses/",
        json={"name": "October Phone Bill", "amount": 100.0, "category": "Utilities", "created_at": "2026-10-05T12:00:00"},
        headers=auth_user["headers"],
    )
    # Add expense in November
    await client.post(
        "/expenses/",
        json={"name": "November Gadget", "amount": 500.0, "category": "Electronics", "created_at": "2026-11-01T12:00:00"},
        headers=auth_user["headers"],
    )

    # Check October monthly totals
    res_oct = await client.get("/totals/month/2026/10/", headers=auth_user["headers"])
    assert res_oct.status_code == 200
    oct_data = res_oct.json()
    assert oct_data["year"] == 2026
    assert oct_data["month"] == 10
    assert oct_data["total_expense"] == 100.0
    assert oct_data["total_salary"] == 4000.0
    assert oct_data["remaining_amount"] == 3900.0


@pytest.mark.asyncio
async def test_totals_user_isolation(
    client: AsyncClient, auth_user: dict, second_user: dict
):
    """Test that financial totals are strictly isolated between different users."""
    # User 1 adds salary & expense
    await client.post(
        "/salary/",
        json={"amount": 3000.0},
        headers=auth_user["headers"],
    )
    await client.post(
        "/expenses/",
        json={"name": "User 1 Coffee", "amount": 50.0, "category": "Food"},
        headers=auth_user["headers"],
    )

    # User 2 adds salary & expense
    await client.post(
        "/salary/",
        json={"amount": 7000.0},
        headers=second_user["headers"],
    )
    await client.post(
        "/expenses/",
        json={"name": "User 2 Laptop", "amount": 2000.0, "category": "Work"},
        headers=second_user["headers"],
    )

    # Verify User 1 totals
    res1 = await client.get("/totals/", headers=auth_user["headers"])
    assert res1.json()["total_expense"] == 50.0
    assert res1.json()["total_salary"] == 3000.0
    assert res1.json()["remaining_amount"] == 2950.0

    # Verify User 2 totals
    res2 = await client.get("/totals/", headers=second_user["headers"])
    assert res2.json()["total_expense"] == 2000.0
    assert res2.json()["total_salary"] == 7000.0
    assert res2.json()["remaining_amount"] == 5000.0
