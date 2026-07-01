import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID  # ADMIN_ID ከ config ፋይል ይመጣል

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()

@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("🔗 ማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def check_channel(message: Message, state: FSMContext, bot: Bot):
    channel_link = message.text.replace("https://t.me/", "@")
    try:
        chat = await bot.get_chat(channel_link)
        # አድሚን መሆኑን ማረጋገጥ
        member = await bot.get_chat_member(chat.id, bot.id)
        if member.status not in ['administrator', 'creator']:
            return await message.answer("❌ ቦቱ ቻናሉ ውስጥ አድሚን አይደለም። እባክህ 'Administrator' አድርገህ እንደገና ሞክር።")
        
        await state.update_data(link=channel_link, chat_id=chat.id)
        await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)")
        await state.set_state(AdvertiseState.waiting_for_members)
    except Exception as e:
        await message.answer(f"❌ ቻናሉን ማግኘት አልቻልኩም። ሊንኩ ትክክል መሆኑን እና ቦቱ ቻናሉ ውስጥ መኖሩን ያረጋግጡ።")

@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit() or int(message.text) < 10:
        return await message.answer("❌ እባክህ ትክክለኛ ቁጥር ላክ (ቢያንስ 10 ሰው መሆን አለበት)።")
    
    members = int(message.text)
    total_price = members * 0.5
    data = await state.get_data()
    
    # ዳታቤዝ ላይ ማስቀመጥ
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, 'pending')",
                    (message.from_user.id, data['link'], members, total_price))
        conn.commit()
    conn.close()
    
    # ለተጠቃሚው ማሳወቅ
    await message.answer(f"✅ ማስታወቂያዎ በተሳካ ሁኔታ ተመዝግቧል! አድሚን ሲያጸድቀው ይጀምራል።\n\n💵 ጠቅላላ ክፍያ: {total_price} ብር።")
    
    # ለአድሚን መላክ (ይህ ክፍል ነው አሁን እየሰራ ያልነበረው)
    try:
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ!\n👤 የተጠቃሚ ID: {message.from_user.id}\n🔗 ቻናል: {data['link']}\n👥 አባላት: {members}\n💰 ክፍያ: {total_price} ብር\n\nእባክዎ ዳታቤዝ ውስጥ ገብተው ያረጋግጡ።")
    except Exception as e:
        print(f"Admin-ን ለማሳወቅ አልተቻለም: {e}")
    
    await state.clear()