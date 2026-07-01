import re
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
async def start_advertise(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Channel", callback_data="adv_channel"),
         InlineKeyboardButton(text="🤖 Bot", callback_data="adv_bot")]
    ])
    await message.answer("📢 ምን ማስተዋወቅ ይፈልጋሉ?", reply_markup=kb)

@router.callback_query(F.data.startswith("adv_"))
async def get_ad_type(callback: CallbackQuery, state: FSMContext):
    adv_type = callback.data.split("_")[1]
    await state.update_data(type=adv_type)
    await callback.message.answer("🔗 ሊንኩን ይላኩ (ለቻናል @username፣ ለቦት ሊንክ):")
    await state.set_state(AdvertiseState.waiting_for_link)
    await callback.answer()

@router.message(AdvertiseState.waiting_for_link)
async def check_link(message: Message, state: FSMContext, bot: Bot):
    link = message.text.strip()
    try:
        # ለቻናልም ለቦትም ሊንኩ መኖሩን ያረጋግጣል
        await bot.get_chat(link)
        await state.update_data(link=link)
        await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)")
        await state.set_state(AdvertiseState.waiting_for_members)
    except Exception as e:
        await message.answer("❌ ቻናሉን/ቦቱን ማግኘት አልቻልኩም። ሊንኩን በትክክል በ @username መልክ ይላኩ።")

@router.message(AdvertiseState.waiting_for_members)
async def process_members(message: Message, state: FSMContext, bot: Bot):
    if not message.text.isdigit() or int(message.text) < 10:
        return await message.answer("❌ ቢያንስ 10 ሰው ማዘዝ አለብዎት። ቁጥር ብቻ ያስገቡ።")
    
    num = int(message.text)
    total_price = num * 0.5
    data = await state.get_data()
    adv_type = data.get('type')
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT amount FROM balances WHERE user_id = %s", (message.from_user.id,))
    row = cur.fetchone()
    balance = row[0] if row else 0
    
    if balance >= total_price:
        cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (total_price, message.from_user.id))
        cur.execute("INSERT INTO ads (user_id, link, target_count, current_count, price, status, type) VALUES (%s, %s, %s, 0, %s, 'active', %s)", 
                    (message.from_user.id, data['link'], num, total_price, adv_type))
        conn.commit()
        await message.answer(f"✅ ማስታወቂያዎ ተጀምሯል!\n💰 {total_price} ብር ተቀንሷል።")
    else:
        user_mention = message.from_user.username
        user_info = f"@{user_mention}" if user_mention else f"ID: {message.from_user.id}"
        
        await message.answer("⚠️ በቂ ባላንስ የለዎትም። እባክዎ @Ariff_Support ያናግሩ።")
        
        # ለአድሚን ማሳወቂያ
        await bot.send_message(
            ADMIN_ID, 
            f"⚠️ **ማስታወቂያ ክፍያ ይፈልጋል!**\n\n"
            f"👤 ተጠቃሚ: {user_info}\n"
            f"🆔 User ID: {message.from_user.id}\n"
            f"💰 የሚፈለግ ክፍያ: {total_price} ብር\n"
            f"🔗 ሊንክ: {data['link']}\n"
            f"📍 አይነት: {adv_type.upper()}" 
        )
        
    conn.close()
    await state.clear()