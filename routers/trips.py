from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import Trip, User
from app.database import get_session, AsyncSession
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import selectinload

class UserResponse(BaseModel):
  id: str
  name: str

  class Config:
      orm_mode = True
class TripResponse(BaseModel):
    id: str
    name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    created_at: datetime
    participants: list[UserResponse] = []

    class Config:
        orm_mode = True
class TripListResponse(BaseModel):
    message: str
    result: list[TripResponse]

class TripCreate(BaseModel):
    name: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    participants: list[str] = []


router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripListResponse)
async def create_trip(trip: TripCreate, session: AsyncSession = Depends(get_session)):
    users = (await session.execute(
        select(User).where(User.id.in_(trip.participants)))
    ).scalars().all()

    trip_obj = Trip(
        name=trip.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        participants=users
    )
    session.add(trip_obj)
    await session.commit()
    result = await session.execute(
        select(Trip)
        .where(Trip.id == trip_obj.id)
        .options(selectinload(Trip.participants))
    )
    trip = result.scalars().first()
    return {"message": "Trip created successfully", "result": [trip]}

@router.get("/", response_model=TripListResponse)
async def list_trips(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Trip).options(selectinload(Trip.participants))
    )
    trips = result.scalars().all()
    return {"message": "Trips retrieved successfully", "result": trips}

@router.get("/{trip_id}", response_model=TripListResponse)
async def get_trip(trip_id: str, session: AsyncSession = Depends(get_session)):
    trip_obj = await session.execute(
        select(Trip).where(Trip.id == trip_id)
        .options(selectinload(Trip.participants))
    )
    trip = trip_obj.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip retrieved successfully", "result": [trip]}