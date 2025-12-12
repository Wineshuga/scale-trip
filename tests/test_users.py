import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    payload = {"name": "Test User", "email": "test@example.com"}
    resp = await client.post("/users/", json=payload)

    assert resp.status_code in (200, 201)

    data = resp.json()
    assert "result" in data
    user = data["result"][0]

    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"
    assert "id" in user


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient):
    payload = {"name": "Dup User", "email": "dup@example.com"}
    resp1 = await client.post("/users/", json=payload)
    assert resp1.status_code in (200, 201)

    resp2 = await client.post("/users/", json=payload)
    assert resp2.status_code in (400, 409)


@pytest.mark.asyncio
async def test_get_user_and_list(client: AsyncClient):
    payload = {"name": "List User", "email": "list@example.com"}
    create_resp = await client.post("/users/", json=payload)
    assert create_resp.status_code in (200, 201)
    created_user = create_resp.json()["result"][0]

    user_id = created_user["id"]

    get_resp = await client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["result"][0]["id"] == user_id

    list_resp = await client.get("/users/")
    assert list_resp.status_code == 200
    listed = list_resp.json()["result"]

    assert any(u["id"] == user_id for u in listed)
