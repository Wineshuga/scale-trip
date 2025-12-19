from typing import Dict, List
from collections import defaultdict
from app.models import Expense
from app.database import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

async def calculate_trip_balances(trip_id: str, session: AsyncSession) -> Dict[str, float]:
    """Return net balance per user. Positive = owed, Negative = owes."""
    balances = defaultdict(float)

    result = await session.execute(
        select(Expense).where(Expense.trip_id == trip_id).options(selectinload(Expense.participants))
    )
    expenses: List[Expense] = result.scalars().all()

    for expense in expenses:
        participants = list({p.id for p in expense.participants} | {expense.payer_id})
        share = expense.amount / len(participants)

        # Credit payer
        balances[expense.payer_id] += expense.amount

        # Subtract each participant's share
        for user_id in participants:
            balances[user_id] -= share

    return balances
