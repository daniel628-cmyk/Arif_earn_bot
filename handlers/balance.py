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
            # ከ amount አምድ ላይ እናንብብ
            cur.execute("SELECT deposit_balance, amount FROM balances WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            
            if not row:
                deposit, earned = 0.0, 0.0
            else:
                deposit = row[0]
                earned = row[1] # እዚህ amount ነው ያለው

            total = deposit + earned
            await message.answer(
                f"💰 **የእርስዎ ባላንስ**\n\n"
                f"📥 ተቀማጭ: **{deposit:.2f}** ብር\n"
                f"💵 የተገኘ (Earned): **{earned:.2f}** ብር\n\n"
                f"🔢 **ጠቅላላ: {total:.2f}** ብር"
            )
    finally:
        conn.close()