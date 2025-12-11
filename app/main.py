from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import trips, users , expenses
from .database import create_db_and_tables

@asynccontextmanager
async def startup(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=startup)

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(expenses.router)

@app.get("/")
async def root():
  return {"message": "Scale-Trip API is running 🚀"}
