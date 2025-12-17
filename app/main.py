from fastapi import FastAPI, Depends, HTTPException, status
from app.auth import oauth2_scheme
from contextlib import asynccontextmanager
from routers import trips, users , expenses
from .database import create_db_and_tables
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.database import get_session, AsyncSession
from pydantic import BaseModel
from app.auth import get_password_hash
from app.schemas import UserResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, Token
from datetime import timedelta
from app.auth import get_current_active_user


@asynccontextmanager
async def startup(app: FastAPI):
  await create_db_and_tables()
  yield

app = FastAPI(lifespan=startup)

class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str

class UserListResponse(BaseModel):
    message: str
    result: list[UserResponse]

app.include_router(users.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(trips.router, dependencies=[Depends(oauth2_scheme)])
app.include_router(expenses.router, dependencies=[Depends(oauth2_scheme)])

@app.get("/")
async def root():
  return {"message": "Scale-Trip API is running 🚀"}

@app.post("/register", response_model=UserListResponse)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)):
    hashed_password = get_password_hash(payload.password)
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hashed_password
    )
    try:
        session.add(user)
        await session.commit()
        result = await session.execute(
            select(User)
            .options(
                selectinload(User.trips),
                selectinload(User.expenses_created),
                selectinload(User.expenses),
            )
            .where(User.id == user.id)
        )
        user_loaded = result.scalars().first()
        return {"message": "User created successfully", "result": [user_loaded]}
    except IntegrityError as e:
        await session.rollback()
        if "ix_user_email" in str(e) or "unique constraint" in str(e).lower():
            raise HTTPException(status_code=409, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Database constraint violation")

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_session)
) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user
