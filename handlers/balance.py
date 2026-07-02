from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Get balances
            cur.execute("""
                SELECT 
                    COALESCE(deposit_balance, 0) as deposit,
                    COALESCE(earned_balance, 0) as earned
                FROM balances 
                WHERE user_id = %s
            """, (user