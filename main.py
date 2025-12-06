from fastapi import FastAPI

app = FastAPI()

trips = []

@app.get("/")
def root():
  return {"Hello": "World"}

@app.get("/trips/")
def get_trips():
  return {"trips": trips}

@app.post("/trips/")
def create_trip(trip: dict):
  trips.append(trip)
  return {"trips": trips}

