from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT deposit_balance, earned_balance 
            FROM balances WHERE user_id = %s
        """, (user_id,))
        row = cur.fetchone()
    conn.close()

    if not row:
        deposit = earned = 0.0
    else:
        deposit, earned = row

    await message.answer(
        f"💰 **Your Balance**\n\n"
        f"📥 Deposit: **{deposit:.2f}** Birr\n"
        f"💵 Earned: **{earned:.2f}** Birr\n"
        f"🔢 Total: **{deposit + earned:.2f}** Birr"
    )