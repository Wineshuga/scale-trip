from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from routers import trips, users , expenses
from .database import create_db_and_tables
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.schemas import UserMini

@asynccontextmanager
async def startup(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=startup)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_decode_token(token):
    return UserMini(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[UserMini, Depends(get_current_user)]):
    return current_user

app.include_router(users.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(trips.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(expenses.router, dependencies=[Depends(oauth2_scheme)])

@app.get("/")
async def root():
  return {"message": "Scale-Trip API is running 🚀"}


