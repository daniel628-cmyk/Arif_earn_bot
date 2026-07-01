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

@router.message(F.text == "📣 Advertise")
async def advertise_menu(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Channel", callback_data="adv_type_channel"),
         InlineKeyboardButton(text="🤖 Bot", callback_data="adv_type_bot")]
    ])
    await message.answer("📢 ምን ማስተዋወቅ ይፈልጋሉ?", reply_markup=kb)

@router.callback_query(F.data.startswith("adv_type_"))
async def set_type(call: CallbackQuery, state: FSMContext):
    adv_type = call.data.split("_")[2]
    await state.update_data(adv_type=adv_type)
    
    if adv_type == 'channel':
        await call.message.answer("🔗 ቻናሉ ላይ Bot Admin ያድርጉ። ከዛ ቻናል ሊንክ (ለምሳሌ @username) ይላኩ።")
        await state.set_state(AdvertiseState.waiting_for_link)
    else:
        await call.message.answer("🔎 ማስተዋወቅ የሚፈልጉትን የቦት Message Forward ያድርጉ:")
        await state.set_state(AdvertiseState.waiting_for_bot_msg)
    await call.answer()

# ቻናል ማረጋገጫ (Admin Check)
@router.message(AdvertiseState.waiting_for_link)
async def check_link(message: Message, state: FSMContext, bot: Bot):
    link = message.text.replace("https://t.me/", "@")
    try:
        chat = await bot.get_chat(link)
        member = await bot.get_chat_member(chat.id, bot.id)
        if member.status not in ['administrator', 'creator']:
            return await message.answer("❌ ቦቱ ቻናሉ ውስጥ አድሚን አይደለም። እባክህ 'Administrator' አድርገህ እንደገና ሞክር።")
        
        await state.update_data(link=link)
        await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)")
        await state.set_state(AdvertiseState.waiting_for_members)
    except Exception as e:
        await message.answer("❌ ቻናሉን ማግኘት አልቻልኩም። ሊንኩን በትክክል መላክዎን ያረጋግጡ።")

# ማጠቃለያ እና አድሚን ማሳወቂያ
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
    
    # ለአድሚን ማሳወቅ (በዚህ ክፍል ነው አድሚን ጋር መድረስ ያለበት)
    try:
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ!\n👤 User: {message.from_user.id}\n📍 አይነት: {data['adv_type']}\n🔗 Link: {data['link']}\n👥 አባላት: {members}\n💰 ክፍያ: {total_price} ብር")
    except Exception as e:
        print(f"Error sending to admin: {e}")
    
    await state.clear()