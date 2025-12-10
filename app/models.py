from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid

class TripParticipant(SQLModel, table=True):
  trip_id: str = Field(default=None, foreign_key="trip.id", primary_key=True)
  user_id: str = Field(default=None, foreign_key="user.id", primary_key=True)

class User(SQLModel, table=True):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  name: str
  email: str = Field(unique=True, index=True)
  wallet_balance: float = 0.0
  created_at: datetime = Field(default_factory=datetime.now)

  trips: List["Trip"] = Relationship(back_populates="participants", link_model=TripParticipant)

class Trip(SQLModel, table=True):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  name: str
  start_date: Optional[datetime] = None
  end_date: Optional[datetime] = None
  created_at: datetime = Field(default_factory=datetime.now)

  participants: List[User] = Relationship(back_populates="trips", link_model=TripParticipant)
  expenses: List["Expense"] = Relationship(back_populates="trip")

class Expense(SQLModel, table=True):
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  trip_id: str = Field(foreign_key="trip.id")
  description: str
  amount: float
  date: datetime
  note: Optional[str] = None
  created_at: datetime = Field(default_factory=datetime.now)

  trip: Optional[Trip] = Relationship(back_populates="expenses")
