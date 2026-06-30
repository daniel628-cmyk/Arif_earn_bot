from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

# ይህ መስመር የግድ መኖር አለበት!
router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_amount = State()

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
        await message.answer("❌ እባክህ ቁጥር ብቻ ላክ (ለምሳሌ፡ 50)።")
        return

    data = await state.get_data()
    link = data.get('link')
    user_id = message.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        # የባላንስ ማረጋገጫ
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        user_balance = res[0] if res else 0

        if user_balance >= amount:
            status = 'active'
            cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (amount, user_id))
            await message.answer("✅ ባላንስ ስላለህ ማስታወቂያህ በአውቶማቲክ ተጠናቋል!")
        else:
            status = 'pending'
            await message.answer("⚠️ ባላንስህ በቂ ስላልሆነ ማስታወቂያህ በአድሚን እስኪጸድቅ ይጠብቃል።")
        
        cur.execute(
            "INSERT INTO ads (user_id, link, price, status, target_count) VALUES (%s, %s, %s, %s, 100) RETURNING id",
            (user_id, link, amount, status)
        )
        ad_id = cur.fetchone()[0]
        conn.commit()
    conn.close()

    if status == 'pending':
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ! ID: {ad_id}\nባላንስ የለውም፣ ይገምግሙ።")

    await state.clear()