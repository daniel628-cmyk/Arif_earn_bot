from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db

router = Router()

# 1. መጀመሪያ State-ዎችን መግለፅ
class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_amount = State()

# 2. ከዚያ በኋላ Handler-ዎችን መጻፍ
@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ወይም የቦት ሊንክ ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("✅ ሊንኩ ተይዟል። አሁን ማውጣት የሚፈልጉትን የገንዘብ መጠን (price) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_amount)

@router.message(AdvertiseState.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext):
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
        # ማስታወቂያውን ወደ ዳታቤዝ ማስገባት
        cur.execute(
            "INSERT INTO ads (user_id, link, price, status) VALUES (%s, %s, %s, 'pending')",
            (user_id, link, amount)
        )
        conn.commit()
    conn.close()
    
    await message.answer("✅ ማስታወቂያዎ በተሳካ ሁኔታ ለአድሚን ተልኳል።")
    await state.clear()