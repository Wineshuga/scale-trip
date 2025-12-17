from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from routers import trips, users , expenses
from .database import create_db_and_tables
from fastapi.security import OAuth2PasswordBearer

@asynccontextmanager
async def startup(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=startup)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(users.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(trips.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(expenses.router, dependencies=[Depends(oauth2_scheme)])

@app.get("/")
async def root():
  return {"message": "Scale-Trip API is running 🚀"}
