from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from app.models import Expense, User, Trip
from app.database import get_session, AsyncSession
from typing import List, Optional
from sqlmodel import select
from datetime import datetime
from sqlalchemy.orm import selectinload
from app.schemas import ExpensesListResponse, ExpenseCreate
from app.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])

@router.post("/", response_model=ExpensesListResponse)
async def create_expense(expense_in: ExpenseCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
  # Load the trip and use its participants as the expense participants
  trip_result = await session.execute(
      select(Trip).where(Trip.id == expense_in.trip_id).options(selectinload(Trip.participants))
  )

  trip = trip_result.scalars().first()
  if not trip:
    raise HTTPException(status_code=404, detail="Trip not found")

  expense_obj = Expense(
    trip_id=expense_in.trip_id,
    description=expense_in.description,
    amount=expense_in.amount,
    date=expense_in.date,
    note=expense_in.note,
    participants=trip.participants,
    payer_id=current_user.id
  )
  session.add(expense_obj)
  await session.commit()
  result = await session.execute(
        select(Expense)
        .where(Expense.id == expense_obj.id)
        .options(selectinload(Expense.participants), 
                 selectinload(Expense.paid_by))
    )
  expense = result.scalars().first()
  return {"message": "Expense created successfully", "result": [expense]}

@router.get("/", response_model=ExpensesListResponse)
async def list_expenses(session: AsyncSession = Depends(get_session)):
  result = await session.execute(
    select(Expense).options(selectinload(Expense.participants),
                            selectinload(Expense.paid_by))
  )
  expenses = result.scalars().all()
  return {"message": "Expenses retrieved successfully", "result": expenses}

@router.get("/{expense_id}", response_model=ExpensesListResponse)
async def get_expense(expense_id: str, session: AsyncSession = Depends(get_session)):
  result = await session.execute(
      select(Expense)
      .where(Expense.id == expense_id)
      .options(selectinload(Expense.participants), 
             selectinload(Expense.paid_by))
  )
  
  expense = result.scalars().first()
  if not expense:
    raise HTTPException(status_code=404, detail="Expense not found")
  return {"message": "Expense retrieved successfully", "result": [expense]}

@router.get("/trip/{trip_id}", response_model=ExpensesListResponse)
async def get_expenses_per_trip(trip_id: str, session: AsyncSession = Depends(get_session)):
  result = await session.execute(
      select(Expense)
      .where(Expense.trip_id == trip_id)
      .options(selectinload(Expense.participants), selectinload(Expense.paid_by))
  )
  expenses = result.scalars().all()
  return {"message": "Expenses retrieved successfully", "result": expenses}