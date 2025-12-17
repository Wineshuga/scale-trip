from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped

class TripParticipant(SQLModel, table=True):
  """Junction table: User participation in Trip"""
  trip_id: str = Field(default=None, foreign_key="trip.id", primary_key=True)
  user_id: str = Field(default=None, foreign_key="user.id", primary_key=True)

class ExpenseParticipant(SQLModel, table=True):
  """Junction table: User participation in Expense split"""
  expense_id: str = Field(default=None, foreign_key="expense.id", primary_key=True)
  user_id: str = Field(default=None, foreign_key="user.id", primary_key=True)

class User(SQLModel, table=True):
  """User in the travel cost-sharing app"""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  username: str
  full_name: str
  email: str = Field(unique=True, index=True)
  wallet_balance: float = 0.0
  disabled: Optional[bool] = None
  created_at: datetime = Field(default_factory=datetime.now)

  trips: Mapped[List["Trip"]] = Relationship(back_populates="participants", link_model=TripParticipant)
  
  expenses_created: Mapped[List["Expense"]] = Relationship(back_populates="creator")
  
  expenses: Mapped[List["Expense"]] = Relationship(back_populates="participants", link_model=ExpenseParticipant)


class Trip(SQLModel, table=True):
  """Trip with participants and expenses"""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  name: str
  destination: Optional[str] = None
  budget: Optional[float] = None
  start_date: Optional[datetime] = None
  end_date: Optional[datetime] = None
  created_at: datetime = Field(default_factory=datetime.now)

  participants: Mapped[List[User]] = Relationship(back_populates="trips", link_model=TripParticipant)
  
  expenses: Mapped[List["Expense"]] = Relationship(back_populates="trip", cascade_delete=True)


class Expense(SQLModel, table=True):
  """Expense split among trip participants"""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
  trip_id: str = Field(foreign_key="trip.id")
  creator_id: str = Field(foreign_key="user.id")
  description: str
  amount: float
  date: datetime
  note: Optional[str] = None
  created_at: datetime = Field(default_factory=datetime.now)

  trip: Mapped[Trip] = Relationship(back_populates="expenses")
  
  creator: Mapped[User] = Relationship(back_populates="expenses_created")
  
  participants: Mapped[List[User]] = Relationship(back_populates="expenses", link_model=ExpenseParticipant)
  
