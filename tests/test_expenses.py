import pytest
from tests.utils import create_user_and_trip
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
async def test_create_expense(client: AsyncClient):
  user, created_trip = await create_user_and_trip(client)

  payload = {
    "trip_id": created_trip["id"],
    "description": "describing",
    "amount": 1000,
    "date": "2025-12-11T01:42:23.603586",
    "note": "note",
  }

  resp = await client.post("/expenses/", json=payload)
  assert resp.status_code in (200, 201)

  data = resp.json()
  assert "result" in data
  expense = data["result"][0]

  assert expense["trip_id"] == created_trip["id"]
  assert expense["participants"]
  assert "created_by" in expense
  
