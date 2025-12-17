# app/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class UserMini(BaseModel):
    id: str
    username: str
    full_name: str
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ExpenseMini(BaseModel):
    id: str
    description: str
    amount: float
    date: datetime

    model_config = ConfigDict(from_attributes=True)

class TripResponse(BaseModel):
    id: str
    name: str
    budget: float | None = None
    destination: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    participants: List[UserMini] = []
    expenses: List[ExpenseMini] = []

    model_config = ConfigDict(from_attributes=True)

class ExpenseResponse(BaseModel):
    id: str
    trip_id: str
    description: str
    amount: float
    date: datetime
    note: Optional[str]
    created_by: Optional[UserMini] = None
    participants: List[UserMini] = []

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    disabled: Optional[bool]
    wallet_balance: float
    created_at: datetime
    trips: List[TripResponse] = []
    expenses_created: List[ExpenseMini] = []
    expenses_participating: List[ExpenseMini] = []

    model_config = ConfigDict(from_attributes=True)
