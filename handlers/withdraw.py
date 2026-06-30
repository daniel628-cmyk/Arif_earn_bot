from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💸 Withdraw")
async def withdraw_request(message: Message):
    user_id = message.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        amount = res[0] if res else 0
        
    conn.close()

    if amount < 50: # ለምሳሌ ዝቅተኛው መውጫ 50 ብር ከሆነ
        await message.answer(f"❌ ቢያንስ 50 ብር ሊኖርዎት ይገባል። የእርስዎ ባላንስ፡ {amount} ብር ነው።")
    else:
        await message.answer("✅ የባንክ አካውንት ቁጥርዎን ወይም ስልክ ቁጥርዎን ይላኩ። ጥያቄዎ በአድሚን ይታያል።")
        # እዚህ ጋር ተጠቃሚው መረጃውን ሲልክ የሚይዝ ሌላ state መጠቀም ይቻላል