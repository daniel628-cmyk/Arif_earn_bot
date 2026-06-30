from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID  # ADMIN_ID በ config.py ውስጥ መኖር አለበት

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_amount = State()

# F.text.contains("Advertise") - 📢 የሚለው ምልክት ቢኖርም ባይኖርም "Advertise" የሚለውን ቃል ብቻ ይፈልጋል
@router.message(F.text.contains("Advertise"))
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ወይም የቦት ሊንክ ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("✅ ሊንኩ ተይዟል። አሁን ማውጣት የሚፈልጉትን የገንዘብ መጠን (price) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_amount)

@router.message(AdvertiseState.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext, bot: Bot):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ እባክዎን ቁጥር ብቻ ይላኩ (ለምሳሌ፡ 50)።")
        return

    data = await state.get_data()
    link = data.get('link')
    user_id = message.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        # ማስታወቂያውን አስገባ (RETURNING id ለAdmin ማሳወቂያ ያስፈልጋል)
        cur.execute(
            "INSERT INTO ads (user_id, link, price, status) VALUES (%s, %s, %s, 'pending') RETURNING id",
            (user_id, link, amount)
        )
        ad_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    
    # አድሚን ጋር ማሳወቂያ ላክ
    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📢 **አዲስ ማስታወቂያ አለ!**\n\n🆔 ID: {ad_id}\n👤 ተጠቃሚ: {user_id}\n🔗 ሊንክ: {link}\n💰 ዋጋ: {amount} ብር\n\nማጽደቂያ: /approve {ad_id}"
        )
    except Exception as e:
        print(f"Error sending to admin: {e}")
    
    await message.answer("✅ ማስታወቂያዎ በተሳካ ሁኔታ ለአድሚን ተልኳል።")
    await state.clear()