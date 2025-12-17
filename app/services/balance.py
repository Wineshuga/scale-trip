from collections import defaultdict
from app.models import Trip

def compute_trip_balances(trip: Trip) -> dict[str, float]:
  balances = defaultdict(float)

  for expense in trip.expenses:
    participants = expense.participants
    num_participants = len(participants)

    if num_participants == 0:
      continue

    share = expense.amount / num_participants

    for user in participants:
      balances[user.id] -= share

    balances[expense.creator_id] += expense.amount

    return dict(balances)