from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()

# 1. መጀመሪያ ተጠቃሚው እንዲመርጥ ማድረግ
@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Channel", callback_data="adv_channel")],
        [InlineKeyboardButton(text="🤖 Bot", callback_data="adv_bot")]
    ])
    await message.answer("📢 ምን ማስተዋወቅ ይፈልጋሉ? ከታች ካሉት አማራጮች ይምረጡ፡", reply_markup=keyboard)

# 2. ምርጫውን ሲጫን
@router.callback_query(F.data.startswith("adv_"))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    adv_type = callback.data.split("_")[1] # channel ወይም bot
    await state.update_data(adv_type=adv_type)
    
    await callback.message.edit_text(f"✅ {adv_type.upper()} መርጠዋል።\n🔗 ማስተዋወቅ የሚፈልጉትን ሊንክ ይላኩ፡")
    await state.set_state(AdvertiseState.waiting_for_link)
    await callback.answer()

# 3. ሊንክ መቀበል እና ቻናል ከሆነ አድሚንነት ማረጋገጥ
@router.message(AdvertiseState.waiting_for_link)
async def check_link(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    link = message.text.replace("https://t.me/", "@")
    
    if data['adv_type'] == 'channel':
        try:
            chat = await bot.get_chat(link)
            member = await bot.get_chat_member(chat.id, bot.id)
            if member.status not in ['administrator', 'creator']:
                return await message.answer("❌ ቦቱ ቻናሉ ውስጥ አድሚን አይደለም። እባክህ 'Administrator' አድርገህ እንደገና ሞክር።")
        except Exception as e:
            return await message.answer("❌ ቻናሉን ማግኘት አልቻልኩም። ሊንኩን በትክክል መላክዎን ያረጋግጡ።")
            
    await state.update_data(link=link)
    await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)")
    await state.set_state(AdvertiseState.waiting_for_members)

# 4. የሰዎች ብዛት እና ማጠቃለያ (አድሚን ማሳወቅ)
@router.message(AdvertiseState.waiting_for_members)
async def finalize_ad(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit() or int(message.text) < 10:
        return await message.answer("❌ እባክህ ትክክለኛ ቁጥር ላክ (ቢያንስ 10 ሰው)።")
    
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
    
    await message.answer(f"✅ ማስታወቂያዎ ለ{data['adv_type']} ተመዝግቧል! አድሚን ሲያጸድቀው ይጀምራል።\n\n💵 ጠቅላላ ክፍያ: {total_price} ብር።")
    
    # ለአድሚን ማሳወቅ
    try:
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ!\n👤 User: {message.from_user.id}\n📍 አይነት: {data['adv_type']}\n🔗 Link: {data['link']}\n👥 አባላት: {members}\n💰 ክፍያ: {total_price} ብር")
    except:
        pass
    
    await state.clear()