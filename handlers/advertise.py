from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

# 1. Router ማስተካከል
router = Router()

# 2. State መግለጽ (ይህ ነው የጠፋው!)
class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()
    waiting_for_price = State()

@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("👥 ምን ያህል ተጠቃሚዎች (Members) እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 9)")
    await state.set_state(AdvertiseState.waiting_for_members)

@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 9:
        return await message.answer("❌ እባክዎ ትክክለኛ ቁጥር ይላኩ (ቢያንስ 9)።")
    await state.update_data(members=int(message.text))
    await message.answer("💰 ለአንድ ሰው ምን ያህል መክፈል ይፈልጋሉ? (ለምሳሌ: 0.5)")
    await state.set_state(AdvertiseState.waiting_for_price)

@router.message(AdvertiseState.waiting_for_price)
async def get_price(message: Message, state: FSMContext, bot: Bot):
    try:
        price = float(message.text)
    except:
        return await message.answer("❌ እባክዎ ቁጥር ብቻ ላክ።")
    
    data = await state.get_data()
    total_price = data['members'] * price
    
    # ዳታቤዝ ላይ ማስቀመጥ
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, 'pending')",
            (message.from_user.id, data['link'], data['members'], total_price)
        )
        conn.commit()
    conn.close()
    
    await message.answer(f"✅ ማስታወቂያህ ለአድሚን ተልኳል። ጠቅላላ ክፍያ: {total_price} ብር።")
    await state.clear()