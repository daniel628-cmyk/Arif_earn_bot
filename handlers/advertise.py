import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()
    waiting_for_confirm = State()

# 1. ቴሌግራም ሊንክ ማረጋገጫ Function
def is_valid_telegram_link(link):
    pattern = r"^(https?://)?(t\.me/|telegram\.me/)([a-zA-Z0-9_]+)$"
    return re.match(pattern, link) is not None

@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ (ለምሳሌ: https://t.me/username) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    if not is_valid_telegram_link(message.text):
        return await message.answer("❌ ትክክለኛ የቴሌግራም ሊንክ አይደለም። እባክህ እንደገና ሞክር።")
    
    await state.update_data(link=message.text)
    await message.answer("👥 ስንት ሰው እንዲገባ ይፈልጋሉ? (ቢያንስ 9 ሰው)")
    await state.set_state(AdvertiseState.waiting_for_members)

@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit() or int(message.text) < 9:
        return await message.answer("❌ እባክህ ቁጥር ብቻ ላክ (ቢያንስ 9 መሆን አለበት)።")
    
    members = int(message.text)
    price_per_user = 0.5
    total_price = members * price_per_user
    
    await state.update_data(members=members, total=total_price)
    
    # የባላንስ ማረጋገጫ
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (message.from_user.id,))
        res = cur.fetchone()
        user_balance = res[0] if res else 0
    conn.close()

    if user_balance >= total_price:
        status = 'active'
        await message.answer(f"✅ ባላንስ ስላለህ ማስታወቂያህ በራስ-ሰር ተጀምሯል!\nጠቅላላ ክፍያ: {total_price} ብር ተቀንሷል።")
        # ከባላንስ ቀንስ
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (total_price, message.from_user.id))
            cur.execute("INSERT INTO ads (user_id, link, target_count, status) VALUES (%s, %s, %s, %s)", 
                        (message.from_user.id, (await state.get_data())['link'], members, status))
            conn.commit()
        conn.close()
    else:
        status = 'pending'
        await message.answer(f"⚠️ ባላንስህ በቂ ስላልሆነ ማስታወቂያህ ለአድሚን ተልኳል።\nጠቅላላ ክፍያ: {total_price} ብር።\n\nእባክህ ክፍያውን ከፈጸምክ በኋላ በአድሚን በኩል ባላንስ እንዲጨመርልህ አናግረን።")
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ! ተጠቃሚ {message.from_user.id}፣ ክፍያ: {total_price} ብር።")
        
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO ads (user_id, link, target_count, status) VALUES (%s, %s, %s, %s)", 
                        (message.from_user.id, (await state.get_data())['link'], members, status))
            conn.commit()
        conn.close()

    await state.clear()