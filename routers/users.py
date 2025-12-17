from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.orm import selectinload
from app.models import User
from app.database import get_session, AsyncSession
from pydantic import BaseModel
from app.schemas import UserResponse
class UserListResponse(BaseModel):
    message: str
    result: list[UserResponse]

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=UserListResponse)
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).options(
            selectinload(User.trips),
            selectinload(User.expenses_created),
            selectinload(User.expenses),
        )
    )
    users = result.scalars().all()
    return {"message": "Users retrieved successfully", "result": users}

@router.get("/{user_id}", response_model=UserListResponse)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(User).options(
            selectinload(User.trips),
            selectinload(User.expenses_created),
            selectinload(User.expenses),
        ).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User retrieved successfully", "result": [user]}