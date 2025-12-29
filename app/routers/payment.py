from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import User, Payment
from app.database import get_session, AsyncSession
from app.schemas import WalletResponse, WalletBalanceResponse, TopupRequest, PaymentRequest

router = APIRouter(prefix="/wallet", tags=["Wallet"])

# get payer id, payee id, trip id, amount from Settlement calculation

@router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet(user_id: str, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    payments = await session.execute(
        select(Payment)
        .where(Payment.payer_id == user_id or Payment.payee_id == user_id)
    )
    payments_list = payments.scalars().all()

    return WalletResponse(
        balance=user.wallet_balance,
        transactions=payments_list
    )

@router.post("/topup-request")
async def request_top_up(payload: TopupRequest, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # create a payment request with Paystack's API
    # use amount in naira
    # integrate paystack

    return {"message": "Top-up initiated", "payment_link": "https://paystack.mock/"}

@router.post("/confirm", response_model=WalletBalanceResponse)
async def top_up_wallet(payload: TopupRequest, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Here, you would verify the payment with Paystack's API
    user.wallet_balance += payload.amount # in kobo
    user.wallet_balance_in_naira = user.wallet_balance / 100
    await session.commit()
    await session.refresh(user)

    return WalletBalanceResponse(
        message="Wallet topped up successfully",
        balance=[
            {"naira": user.wallet_balance_in_naira},
            {"kobo": user.wallet_balance}
        ]
    )

@router.post("/pay", response_model=WalletBalanceResponse)
async def pay_from_wallet(payload: PaymentRequest, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, payload.payer_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.wallet_balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    user.wallet_balance -= payload.amount

    payee = await session.get(User, payload.payee_id)
    if not payee:
        raise HTTPException(status_code=404, detail="Payee not found")
    payee.wallet_balance += payload.amount # in kobo
    payee.wallet_balance_in_naira = payee.wallet_balance / 100

    payment_record = Payment(
        trip_id=payload.trip_id,
        payer_id=payload.payer_id,
        payee_id=payload.payee_id,
        amount=payload.amount,
        amount_in_naira=payload.amount / 100
    )
    session.add(payment_record)
    await session.commit()
    await session.refresh(user)

    return WalletBalanceResponse(
        message="Payment successful",
        balance=[
            {"naira": user.wallet_balance_in_naira},
            {"kobo": user.wallet_balance}
        ]
    )