import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_expense_unauthenticated(client:AsyncClient):
    payload={"name":"Coffee","amount":4.50,"category":"Food"}
    response=await client.post("/expenses/",json=payload)
    assert response.status_code==401

@pytest.mark.asyncio
async def test_list_expenses_unauthenticated(client:AsyncClient):
    response=await client.get("/expenses/")
    assert response.status_code==401

@pytest.mark.asyncio
async def test_create_expense_success(client:AsyncClient,auth_user:dict):
    payload={"name":"Supermarket Grocery","amount":85.50,"category":"Food"}
    response=await client.post("/expenses/",json=payload,headers=auth_user["headers"])
    assert response.status_code==201
    data=response.json()
    assert "expense_id" in data
    assert data["name"]=="Supermarket Grocery"
    assert data["amount"]==85.50
    assert data["category"]=="Food"
    assert "created_at" in data

@pytest.mark.asyncio
async def test_create_expense_validation_error(client:AsyncClient,auth_user:dict):
    res1=await client.post("/expenses/",json={"name":"Bad Item","amount":-10.0,"category":"Food"},headers=auth_user["headers"])
    assert res1.status_code==422
    res2=await client.post("/expenses/",json={"name":"Bad Item","amount":0.0,"category":"Food"},headers=auth_user["headers"])
    assert res2.status_code==422
    res3=await client.post("/expenses/",json={"name":"Bad Item","amount":50.0},headers=auth_user["headers"])
    assert res3.status_code==422

@pytest.mark.asyncio
async def test_list_expenses_success(client:AsyncClient,auth_user:dict):
    await client.post("/expenses/",json={"name":"Dinner","amount":45.0,"category":"Food"},headers=auth_user["headers"])
    await client.post("/expenses/",json={"name":"Bus Pass","amount":60.0,"category":"Transport"},headers=auth_user["headers"])
    response=await client.get("/expenses/",headers=auth_user["headers"])
    assert response.status_code==200
    data=response.json()
    assert len(data)==2
    assert any(e["name"]=="Dinner" for e in data)
    assert any(e["name"]=="Bus Pass" for e in data)

@pytest.mark.asyncio
async def test_get_single_expense(client:AsyncClient,auth_user:dict):
    res_create=await client.post("/expenses/",json={"name":"Laptop Stand","amount":35.0,"category":"Work"},headers=auth_user["headers"])
    expense_id=res_create.json()["expense_id"]
    res_get=await client.get(f"/expenses/{expense_id}",headers=auth_user["headers"])
    assert res_get.status_code==200
    assert res_get.json()["name"]=="Laptop Stand"

@pytest.mark.asyncio
async def test_update_expense(client:AsyncClient,auth_user:dict):
    res_create=await client.post("/expenses/",json={"name":"Gym","amount":50.0,"category":"Health"},headers=auth_user["headers"])
    expense_id=res_create.json()["expense_id"]
    res_update=await client.put(f"/expenses/{expense_id}",json={"amount":55.0,"name":"Gym Premium"},headers=auth_user["headers"])
    assert res_update.status_code==200
    data=res_update.json()
    assert data["amount"]==55.0
    assert data["name"]=="Gym Premium"
    assert data["category"]=="Health"

@pytest.mark.asyncio
async def test_delete_expense(client:AsyncClient,auth_user:dict):
    res_create=await client.post("/expenses/",json={"name":"Old Magazine","amount":5.0,"category":"Leisure"},headers=auth_user["headers"])
    expense_id=res_create.json()["expense_id"]
    res_delete=await client.delete(f"/expenses/{expense_id}",headers=auth_user["headers"])
    assert res_delete.status_code==204
    res_get=await client.get(f"/expenses/{expense_id}",headers=auth_user["headers"])
    assert res_get.status_code==404

@pytest.mark.asyncio
async def test_expense_user_isolation(client:AsyncClient,auth_user:dict,second_user:dict):
    res_create=await client.post("/expenses/",json={"name":"Private Expense","amount":100.0,"category":"Personal"},headers=auth_user["headers"])
    expense_id=res_create.json()["expense_id"]
    res_list2=await client.get("/expenses/",headers=second_user["headers"])
    assert res_list2.status_code==200
    assert len(res_list2.json())==0
    res_get2=await client.get(f"/expenses/{expense_id}",headers=second_user["headers"])
    assert res_get2.status_code==404