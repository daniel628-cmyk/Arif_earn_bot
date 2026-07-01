import re
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()

# 1. ሊንክ መቀበል
@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("🔗 ማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ (ለምሳሌ: @channel_username ወይም https://t.me/...) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

# 2. ቻናል ማረጋገጥ እና መፈለግ
@router.message(AdvertiseState.waiting_for_link)
async def check_channel(message: Message, state: FSMContext, bot: Bot):
    channel_link = message.text.replace("https://t.me/", "@")
    
    try:
        # ቦቱ ቻናሉን እንዲያገኝ መሞከር
        chat = await bot.get_chat(channel_link)
        
        # ቦቱ አድሚን መሆኑን ማረጋገጥ
        member = await bot.get_chat_member(chat.id, bot.id)
        if member.status not in ['administrator', 'creator']:
            return await message.answer("❌ ቦቱ ቻናሉ ውስጥ አድሚን አይደለም። እባክህ መጀመሪያ 'Administrator' አድርገህ እንደገና ሞክር።")
        
        await state.update_data(link=channel_link, chat_id=chat.id)
        await message.answer(f"✅ ቻናል ተገኝቷል: {chat.title}\n\n💸 ምን ያህል ሰው እንዲቀላቀሉ ይፈልጋሉ? (ለአንድ ሰው 0.5 ብር)")
        await state.set_state(AdvertiseState.waiting_for_members)
        
    except Exception as e:
        await message.answer(f"❌ ቻናሉን ማግኘት አልቻልኩም! \nምክንያት: ሊንኩ ስህተት ሊሆን ይችላል ወይም ቦቱ ቻናሉ ውስጥ የለም።\nእባክህ ሊንኩን በትክክል መላክህን አረጋግጥ።")

# 3. የሰዎች ብዛት እና ዋጋ ስሌት
@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 1:
        return await message.answer("❌ እባክህ ትክክለኛ ቁጥር ላክ (ቢያንስ 1 ሰው)።")
    
    members = int(message.text)
    total_price = members * 0.5
    
    data = await state.get_data()
    
    await message.answer(f"🎉 ማስታወቂያዎ ተመዝግቧል!\n\n"
                         f"🔗 ቻናል: {data['link']}\n"
                         f"💰 አጠቃላይ ተጠቃሚዎች: {members}\n"
                         f"💵 አጠቃላይ ክፍያ: {total_price} ብር\n\n"
                         f"✅ ማስታወቂያው አሁን ወደ አድሚን ተልኳል።")
    
    # ዳታቤዝ ላይ ማስቀመጥ (status='pending')
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, 'pending')",
                    (message.from_user.id, data['link'], members, total_price))
        conn.commit()
    conn.close()
    
    await state.clear()