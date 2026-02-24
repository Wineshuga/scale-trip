from typing import Dict, List
from collections import defaultdict
from app.models import Expense, Payment
from app.database import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

async def calculate_trip_balances(trip_id: str, session: AsyncSession) -> Dict[str, int]:
    """Return net balance per user. Positive = owed, Negative = owes."""
    acct_details = []

    result = await session.execute(
        select(Expense).where(Expense.trip_id == trip_id).options(selectinload(Expense.participants))
    )
    expenses: List[Expense] = result.scalars().all()

    payment_details = await session.execute(
        select(Payment).where(Payment.trip_id == trip_id)
    )
    payments: List[Payment] = payment_details.scalars().all()

    for expense in expenses:
        participants = list({p.id for p in expense.participants} | {expense.payer_id})
        num_participants = len(participants)
        base_share = expense.amount // num_participants
        remainder = expense.amount % num_participants

        # Credit payer
        details = {
            "user_id": expense.payer_id,
            "amount": base_share,
            "amount_received": sum(p.amount for p in payments if p.payee_id == expense.payer_id),
            "paid": sum(p.amount for p in payments if p.payer_id == expense.payer_id),
            "balance": base_share - sum(p.amount for p in payments if p.payee_id == expense.payer_id)
        }
        acct_details.append(details)

        # Subtract each participant's share
        for i, user_id in enumerate(participants):
            if user_id == expense.payer_id:
                continue
            details = {
                'user_id': user_id,
                'amount': -(base_share - (1 if i < remainder else 0)),
                "amount_received": sum(p.amount for p in payments if p.payee_id == user_id),
                'paid': sum(p.amount for p in payments if p.payer_id == user_id),
                "balance": expense.amount - sum(p.amount for p in payments if p.payer_id == user_id)
            }
            acct_details.append(details)

    return acct_details

def simplify_balances(acct_details: List[Dict]) -> List[Dict]:
    """Return minimal list of settlements: who pays who and how much."""
    balances = defaultdict(int)
    for detail in acct_details:
        balances[detail["user_id"]] += detail["amount"]

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
