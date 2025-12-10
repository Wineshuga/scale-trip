from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import User
from app.database import async_session, AsyncSession
from pydantic import BaseModel

class UserListResponse(BaseModel):
    message: str
    result: list[User]

router = APIRouter(prefix="/users", tags=["Users"])

# Dependency for async session
async def get_session():
    async with async_session() as session:
        yield session

@router.post("/", response_model=UserListResponse)
async def create_user(user: User, session: AsyncSession = Depends(get_session)):
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "User created successfully", "result": [user]}

@router.get("/", response_model=UserListResponse)
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return {"message": "Users retrieved successfully", "result": users}

@router.get("/{user_id}", response_model=UserListResponse)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User retrieved successfully", "result": [user]}