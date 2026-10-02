from datetime import datetime
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_filter_by_month_endpoint(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"October Rent","amount":1200.0,"category":"Housing","created_at":"2026-10-05T10:00:00"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"October Groceries","amount":250.0,"category":"Food","created_at":"2026-10-18T14:30:00"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"November Books","amount":45.0,"category":"Education","created_at":"2026-11-02T11:00:00"},headers=auth_user["headers"])
    response_oct=await client.get("/expenses/month/2026/10/",headers=auth_user["headers"])
    assert response_oct.status_code==200
    oct_expenses=response_oct.json()
    assert len(oct_expenses)==2
    assert all("2026-10" in e["created_at"] for e in oct_expenses)
    response_nov=await client.get("/expenses/month/2026/11/",headers=auth_user["headers"])
    assert response_nov.status_code==200
    nov_expenses=response_nov.json()
    assert len(nov_expenses)==1
    assert nov_expenses[0]["name"]=="November Books"
    response_empty=await client.get("/expenses/month/2026/1/",headers=auth_user["headers"])
    assert response_empty.status_code==200
    assert len(response_empty.json())==0

@pytest.mark.asyncio
async def test_filter_by_month_validation(client:AsyncClient,auth_user:dict):
    res_bad_month=await client.get("/expenses/month/2026/13/",headers=auth_user["headers"])
    assert res_bad_month.status_code==400
    res_bad_year=await client.get("/expenses/month/1800/5/",headers=auth_user["headers"])
    assert res_bad_year.status_code==400

@pytest.mark.asyncio
async def test_filter_by_week(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"Week 40 Coffee","amount":15.0,"category":"Food","created_at":"2026-10-01T09:00:00"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"Week 42 Gadget","amount":99.0,"category":"Electronics","created_at":"2026-10-15T15:00:00"},headers=auth_user["headers"])
    response=await client.get("/expenses/week/2026/40/",headers=auth_user["headers"])
    assert response.status_code==200
    data=response.json()
    assert len(data)==1
    assert data[0]["name"]=="Week 40 Coffee"

@pytest.mark.asyncio
async def test_filter_by_day(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"Morning Breakfast","amount":12.0,"category":"Food","created_at":"2026-10-01T08:30:00"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"Next Day Lunch","amount":20.0,"category":"Food","created_at":"2026-10-02T13:00:00"},headers=auth_user["headers"])
    response=await client.get("/expenses/day/2026/10/1/",headers=auth_user["headers"])
    assert response.status_code==200
    data=response.json()
    assert len(data)==1
    assert data[0]["name"]=="Morning Breakfast"
    res_bad_date=await client.get("/expenses/day/2026/2/30/",headers=auth_user["headers"])
    assert res_bad_date.status_code==400

@pytest.mark.asyncio
async def test_filter_by_category(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"Subway","amount":10.0,"category":"Food"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"Metro Ticket","amount":5.0,"category":"Transport"},headers=auth_user["headers"])
    response=await client.get("/expenses/category/food/",headers=auth_user["headers"])
    assert response.status_code==200
    data=response.json()
    assert len(data)==1
    assert data[0]["name"]=="Subway"

@pytest.mark.asyncio
async def test_query_parameters_filter(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"Flight Ticket","amount":350.0,"category":"Travel","created_at":"2026-08-15T12:00:00"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"Hotel Booking","amount":200.0,"category":"Travel","created_at":"2026-08-16T15:00:00"},headers=auth_user["headers"])
    response=await client.get("/expenses/?category=travel&year=2026&month=8",headers=auth_user["headers"])
    assert response.status_code==200
    data=response.json()
    assert len(data)==2
    assert all(e["category"]=="Travel" for e in data)