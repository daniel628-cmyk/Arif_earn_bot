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

def is_valid_telegram_link(link):
    pattern = r"^(https?://)?(t\.me/|telegram\.me/)([a-zA-Z0-9_]+)$"
    return re.match(pattern, link) is not None

@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("2️⃣ ማስተዋወቅ የሚፈልጉት ቻነል ላይ Bot Admin ያድርጉ።\nከዛ የቻነሉን Link ያስገቡ:")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def check_channel(message: Message, state: FSMContext, bot: Bot):
    if not is_valid_telegram_link(message.text):
        return await message.answer("❌ ትክክለኛ የቻናል ሊንክ አይደለም።")
    
    try:
        chat = await bot.get_chat(message.text)
        member = await bot.get_chat_member(chat.id, bot.id)
        if member.status not in ['administrator', 'creator']:
            return await message.answer("❌ ቦቱ ቻናሉ ውስጥ አድሚን አይደለም። አድሚን አድርገው ይሞክሩ።")
        
        await state.update_data(link=message.text)
        await message.answer("3️⃣ 💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ?\n(ለአንድ ሰው 0.5 ብር፣ ዝቅተኛ 5 - ከፍተኛ 100 ሰው።)")
        await state.set_state(AdvertiseState.waiting_for_members)
    except:
        await message.answer("❌ ቻናሉን ማግኘት አልቻልኩም።")

@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (5 <= int(message.text) <= 100):
        return await message.answer("❌ እባክህ ከ 5 እስከ 100 ባለው ቁጥር ብቻ ላክ።")
    
    members = int(message.text)
    price_per_user = 0.5
    total_price = members * price_per_user
    
    data = await state.get_data()
    
    # ማጠቃለያ
    await message.answer(f"🎉 ማስታወቂያዎ ተመዝግቧል!\n\n"
                         f"🔗 Link : {data['link']}\n"
                         f"💎 በአንድ ሰው የሚከፍሉት : {price_per_user} ብር\n"
                         f"💰 አጠቃላይ ተጠቃሚዎች : {members}\n"
                         f"💵 አጠቃላይ ክፍያ : {total_price} ብር\n\n"
                         f"✅ አድሚን እንደተመለከተው ይጀምራል።")
    
    # ዳታቤዝ ላይ ማስቀመጥ (pending status)
    # [እዚህ ጋር የዳታቤዝ Insert ኮድህን ተጠቀም]
    
    await state.clear()