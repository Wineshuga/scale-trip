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
async def test_get_trip_and_list(client: AsyncClient):
    _, created_trip = await create_user_and_trip(client)

    list_resp = await client.get("/trips/")
    assert list_resp.status_code in (200, 201)
    data = list_resp.json()
    assert "result" in data
    trips = data["result"]
    assert any(t["id"] == created_trip["id"] for t in trips)

    trip_resp = await client.get(f"/trips/{created_trip['id']}")
    assert trip_resp.status_code in (200, 201)
    trip = trip_resp.json()["result"]
    assert any(t["id"] == created_trip["id"] for t in trip)

