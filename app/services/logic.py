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

def simplify_balances(balances: Dict[str, float]) -> List[Dict]:
    """Return minimal list of settlements: who pays who and how much."""
    debtors = []
    creditors = []

    for user_id, bal in balances.items():
        if bal < 0:
            debtors.append([user_id, -bal])
        elif bal > 0:
            creditors.append([user_id, bal])
    settlements = []
    i = 0
    j = 0

    while i < len(debtors) and j < len(creditors):
        debtor, owe = debtors[i]
        creditor, owed = creditors[j]

        amt = min(owe, owed)

        settlements.append({
            "from": debtor,
            "to": creditor,
            "amount": amt
        })

        owe -= amt
        owed -= amt

        if owe == 0:
            i += 1
        else:
            debtors[i][1] = owe

        if owed == 0:
            j += 1
        else:
            creditors[j][1] = owed

    return settlements
