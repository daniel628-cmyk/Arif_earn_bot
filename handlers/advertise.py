from aiogram import Router, F, Bot  # Bot ን ጨምረን
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID  # የአንተን ID ከ config ፋይል ታመጣለህ

router = Router()

# ... (StatesGroup እዚህ እንዳለ ነው)

@router.message(AdvertiseState.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext, bot: Bot): # bot ን እዚህ አስገባነው
    # ... (የቀድሞ ኮዶች) ...
    
    conn = get_db()
    with conn.cursor() as cur:
        # ማስታወቂያውን አስገባ
        cur.execute("INSERT INTO ads (user_id, link, price, status) VALUES (%s, %s, %s, 'pending') RETURNING id", 
                    (user_id, link, amount))
        ad_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    
    # አሁን ለአድሚን ማሳወቂያ እንልክለታለን
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📢 **አዲስ ማስታወቂያ አለ!**\n\n🆔 ID: {ad_id}\n👤 ተጠቃሚ: {user_id}\n🔗 ሊንክ: {link}\n💰 ዋጋ: {amount} ብር\n\nማጽደቂያ: /approve {ad_id}"
        )
    except Exception as e:
        print(f"Error sending to admin: {e}")
    
    await message.answer("✅ ማስታወቂያዎ በተሳካ ሁኔታ ለአድሚን ተልኳል።")
    await state.clear()