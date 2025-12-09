from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables

@asynccontextmanager
async def startup(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=startup)

@app.get("/")
async def root():
  return {"message": "Scale-Trip API is running 🚀"}
