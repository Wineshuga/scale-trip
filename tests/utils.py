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
