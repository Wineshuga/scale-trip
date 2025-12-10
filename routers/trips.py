from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import Trip
from app.database import async_session, AsyncSession
from pydantic import BaseModel

class TripListResponse(BaseModel):
    message: str
    result: list[Trip]

router = APIRouter(prefix="/trips", tags=["Trips"])

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/", response_model=TripListResponse)
async def create_trip(trip: Trip, session: AsyncSession = Depends(get_session)):
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return {"message": "Trip created successfully", "result": [trip]}

@router.get("/", response_model=TripListResponse)
async def list_trips(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Trip))
    trips = result.scalars().all()
    return {"message": "Trips retrieved successfully", "result": trips}

@router.get("/{trip_id}", response_model=TripListResponse)
async def get_trip(trip_id: str, session: AsyncSession = Depends(get_session)):
    trip = await session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip retrieved successfully", "result": [trip]}