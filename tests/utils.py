async def create_user_and_trip(client):
    user_payload = {
        "name": "userfixture",
        "email": f"fixture@example.com",
    }
    user_resp = await client.post("/users/", json=user_payload)
    user = user_resp.json()["result"][0]

    trip_payload = {
        "name": "fixture trip",
        "budget": 1000,
        "start_date": None,
        "end_date": None,
        "participants": [user["id"]],
    }
    trip_resp = await client.post("/trips/", json=trip_payload)
    trip = trip_resp.json()["result"][0]
    return user, trip

async def create_expenses(client):
    _, created_trip = await create_user_and_trip(client)

    payload1 = {
        "trip_id": created_trip["id"],
        "description": "describing",
        "amount": 1000,
        "date": "2025-12-11T01:42:23.603586",
        "note": "note",
    }
    payload2 = {
        "trip_id": created_trip["id"],
        "description": "describing more",
        "amount": 2000,
        "date": "2025-12-11T01:42:23.603586",
        "note": "note",
    }
    resp1 = await client.post("/expenses/", json=payload1)
    resp2 = await client.post("/expenses/", json=payload2)

    return created_trip

