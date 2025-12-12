from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from app.models import Expense, User
from app.database import get_session, AsyncSession
from typing import List, Optional
from sqlmodel import select
from datetime import datetime
from sqlalchemy.orm import selectinload

class UserResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: str
  name: str

class ExpenseResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  id: str
  trip_id: str
  description: str
  amount: float
  date: datetime
  note: Optional[str]
  participants: List[UserResponse]

class ExpensesListResponse(BaseModel):
  message: str
  result: List[ExpenseResponse]

class ExpenseCreate(BaseModel):
  trip_id: str
  description: str
  amount: float
  date: datetime
  note: Optional[str] = None
  participants: List[str]  

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("/", response_model=ExpensesListResponse)
async def create_expense(expense_in: ExpenseCreate, session: AsyncSession = Depends(get_session)):
  users = (await session.execute(
    select(User).where(User.id.in_(expense_in.participants)))
  ).scalars().all()
  
  expense_obj = Expense(
    trip_id=expense_in.trip_id,
    description=expense_in.description,
    amount=expense_in.amount,
    date=expense_in.date,
    note=expense_in.note,
    participants=users
  )
  session.add(expense_obj)
  await session.commit()
  result = await session.execute(
        select(Expense)
        .where(Expense.id == expense_obj.id)
        .options(selectinload(Expense.participants))
    )
  expense = result.scalars().first()
  return {"message": "Expense created successfully", "result": [expense]}

@router.get("/", response_model=ExpensesListResponse)
async def list_expenses(session: AsyncSession = Depends(get_session)):
  result = await session.execute(
    select(Expense).options(selectinload(Expense.participants))
  )
  expenses = result.scalars().all()
  return {"message": "Expenses retrieved successfully", "result": expenses}

@router.get("/{expense_id}", response_model=ExpensesListResponse)
async def get_expense(expense_id: str, session: AsyncSession = Depends(get_session)):
  result = await session.execute(
      select(Expense)
      .where(Expense.id == expense_id)
      .options(selectinload(Expense.participants))
  )
  
  expense = result.scalars().first()
  if not expense:
    raise HTTPException(status_code=404, detail="Expense not found")
  return {"message": "Expense retrieved successfully", "result": [expense]}

