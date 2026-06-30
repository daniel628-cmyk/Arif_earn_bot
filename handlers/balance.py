from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        # ባላንሱን ፈልግ
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        
        # ተጠቃሚው በዳታቤዝ ከሌለ 0 ይጀምር
        if not res:
            cur.execute("INSERT INTO balances (user_id, amount) VALUES (%s, 0)", (user_id,))
            conn.commit()
            amount = 0
        else:
            amount = res[0]
    conn.close()
    
    await message.answer(f"💰 የአሁኑ ባላንስዎ፡ {amount} ብር ነው")