import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_trip(client: AsyncClient):
  user1 = {
    "name": "user 1",
    "email": "user@email.com"
  }
  user_resp = await client.post("/users/", json=user1)
  user_id = user_resp.json()["result"][0]["id"]

  payload = {
    "name": "trip name",
    "budget": 20000,
    "start_date": None,
    "end_date": None,
    "participants": [user_id]
  }

  resp = await client.post("/trips/", json=payload)
  assert resp.status_code in (200, 201)

  data = resp.json()
  assert "result" in data
  trip = data["result"][0]

  assert trip["name"] == "trip name"
  assert trip["budget"] == 20000
  assert trip["start_date"] == None
  assert trip["end_date"] == None
  assert trip["participants"][0]["id"] == user_id
