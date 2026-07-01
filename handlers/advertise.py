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
    waiting_for_price = State()

def is_valid_telegram_link(link):
    pattern = r"^(https?://)?(t\.me/|telegram\.me/)([a-zA-Z0-9_]+)$"
    return re.match(pattern, link) is not None

@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ (ለምሳሌ: https://t.me/username) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    if not is_valid_telegram_link(message.text):
        return await message.answer("❌ ትክክለኛ የቴሌግራም ሊንክ አይደለም።")
    
    # Duplicate check: ይህ ሊንክ ቀድሞ ተመዝግቧል ወይ?
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM ads WHERE link = %s AND status IN ('pending', 'active')", (message.text,))
        if cur.fetchone():
            conn.close()
            return await message.answer("⚠️ ይህ ቻናል ቀድሞውኑ በማስታወቂያ ሂደት ላይ ነው። ሌላ ሊንክ ይሞክሩ።")
    conn.close()
    
    await state.update_data(link=message.text)
    await message.answer("👥 ስንት ሰው እንዲገባ ይፈልጋሉ? (ቢያንስ 9 ሰው)")
    await state.set_state(AdvertiseState.waiting_for_members)

@router.message(AdvertiseState.waiting_for_price)
async def get_price(message: Message, state: FSMContext, bot: Bot):
    try:
        price = float(message.text)
    except:
        return await message.answer("❌ እባክህ ቁጥር ብቻ ላክ።")
    
    data = await state.get_data()
    total_price = data['members'] * price
    
    conn = get_db()
    with conn.cursor() as cur:
        # ባላንስ ያረጋግጡ
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (message.from_user.id,))
        res = cur.fetchone()
        balance = res[0] if res else 0
        
        if balance >= total_price:
            cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (total_price, message.from_user.id))
            status = 'active'
            msg = "✅ ባላንስ ስላለህ ማስታወቂያህ በራስ-ሰር ተጀምሯል!"
        else:
            status = 'pending'
            msg = f"⚠️ ባላንስህ በቂ ስላልሆነ ማስታወቂያህ ለአድሚን ተልኳል።\n\nእባክህ ክፍያ ከፈጸምክ በኋላ በአድሚን በኩል ባላንስ እንዲጨመርልህ አናግር።"
            await bot.send_message(ADMIN_ID, f"📢 አዲስ Pending ማስታወቂያ!\nተጠቃሚ: {message.from_user.id}\nክፍያ: {total_price} ብር")
        
        cur.execute("INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, %s)",
                    (message.from_user.id, data['link'], data['members'], total_price, status))
        conn.commit()
    conn.close()
    
    await message.answer(msg)
    await state.clear()