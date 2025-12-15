import pytest
from httpx import AsyncClient
from tests.utils import create_user_and_trip


@pytest.mark.asyncio
async def test_create_trip(client: AsyncClient):
    user, trip = await create_user_and_trip(client)

    assert trip["name"] == "fixture trip"
    assert trip["budget"] == 1000
    assert trip["participants"][0]["id"] == user["id"]


@pytest.mark.asyncio
async def test_list_trips(client: AsyncClient):
    user, created_trip = await create_user_and_trip(client)

    resp = await client.get("/trips/")
    assert resp.status_code in (200, 201)

    data = resp.json()
    assert "result" in data
    trips = data["result"]

    assert any(t["id"] == created_trip["id"] for t in trips)
    assert trips[0]["name"] == "fixture trip"
    assert trips[0]["budget"] == 1000
    assert trips[0]["start_date"] == None
    assert trips[0]["end_date"] == None
    assert trips[0]["participants"][0]["id"] == user["id"]
