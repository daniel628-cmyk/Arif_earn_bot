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
            # መጀመሪያ ተጠቃሚው መኖሩን ቼክ እናድርግ
            cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
            res = cur.fetchone()
            
            if res:
                amount = res[0]