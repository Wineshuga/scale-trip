from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import Trip, User
from app.database import get_session, AsyncSession
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy.orm import selectinload
from app.schemas import TripResponse
from typing import Optional
from app.services.logic import calculate_trip_balances, simplify_balances
from app.auth import get_current_user

class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: str
  name: str

class TripListResponse(BaseModel):
    message: str
    result: list[TripResponse]

class TripCreate(BaseModel):
    name: str
    budget: float | None = None
    destination: Optional[str] = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    participants: list[str] = []

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripListResponse)
async def create_trip(trip: TripCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    users = (await session.execute(
        select(User).where(User.id.in_(trip.participants)))
    ).scalars().all()

    trip_obj = Trip(
        name=trip.name,
        budget=trip.budget,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        participants=list(users + [current_user])
    )
    session.add(trip_obj)
    await session.commit()
    result = await session.execute(
        select(Trip)
        .where(Trip.id == trip_obj.id)
        .options(            
            selectinload(Trip.participants),
            selectinload(Trip.expenses)
        )
    )
    trip = result.scalars().first()
    return {"message": "Trip created successfully", "result": [trip]}

@router.get("/", response_model=TripListResponse)
async def list_trips(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Trip).options(
            selectinload(Trip.participants),
            selectinload(Trip.expenses)
        )
    )
    trips = result.scalars().all()
    return {"message": "Trips retrieved successfully", "result": trips}

@router.get("/{trip_id}", response_model=TripListResponse)
async def get_trip(trip_id: str, session: AsyncSession = Depends(get_session)):
    trip_obj = await session.execute(
        select(Trip).where(Trip.id == trip_id)
        .options(
            selectinload(Trip.participants),
            selectinload(Trip.expenses)
        )
    )
    trip = trip_obj.scalars().first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip retrieved successfully", "result": [trip]}

@router.get("/{trip_id}/balances")
async def get_trip_balances(trip_id: str, session: AsyncSession = Depends(get_session)):
    balances = await calculate_trip_balances(trip_id, session)
    settlements = simplify_balances(balances)
    return {
        "message": "Balances retrieved successfully",
        "balances": balances,
        "settlements": settlements
    }
