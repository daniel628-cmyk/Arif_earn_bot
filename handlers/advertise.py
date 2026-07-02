from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID  # ADMIN_ID ከ config ፋይል መምጣቱን አረጋግጥ

router = Router()

# ዋናው ሜኑ (ተጠቃሚው ማስታወቂያ ሲሰርዝ ወይም ሲጨርስ ወደዚህ ይመለሳል)
def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)

# የሰርዝ (Cancel) በተን
def cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Cancel")]], resize_keyboard=True)

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

# ማስታወቂያን ለመሰረዝ የሚያስችል Handler
@router.message(F.text == "❌ Cancel")
async def cancel_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ ማስታወቂያው ተሰርዟል። ዋናው ሜኑ ላይ ነዎት።", reply_markup=get_main_kb())

@router.callback_query(F.data.startswith("adv_"))
async def get_ad_type(callback: CallbackQuery, state: FSMContext):
    adv_type = callback.data.split("_")[1]
    await state.update_data(type=adv_type)
    await callback.message.answer("🔗 ሊንኩን ይላኩ (ለቻናል @username፣ ለቦት ሊንክ):", reply_markup=cancel_kb())
    await state.set_state(AdvertiseState.waiting_for_link)
    await callback.answer()

@router.message(AdvertiseState.waiting_for_link)
async def check_link(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Cancel":
        return await cancel_process(message, state)
        
    link = message.text.strip()
    try:
        await bot.get_chat(link)
        await state.update_data(link=link)
        await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)", reply_markup=cancel_kb())
        await state.set_state(AdvertiseState.waiting_for_members)
    except Exception:
        await message.answer("❌ ቻናሉን/ቦቱን ማግኘት አልቻልኩም። ሊንኩን በትክክል በ @username መልክ ይላኩ።")

@router.message(AdvertiseState.waiting_for_members)
async def process_members(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Cancel":
        return await cancel_process(message, state)
        
    if not message.text.isdigit():
        return await message.answer("❌ እባክዎ ቁጥር ብቻ ያስገቡ።")
    num = int(message.text)
    if num < 10:
        return await message.answer("❌ ቢያንስ 10 ሰው ማዘዝ አለብዎት።")
    
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
        await message.answer(f"✅ ማስታወቂያዎ ተጀምሯል!\n💰 {total_price} ብር ተቀንሷል።", reply_markup=get_main_kb())
    else:
        # ባላንስ በሌለበት ጊዜ ለአድሚን ማሳወቂያ መላክ
        await message.answer("⚠️ በቂ ባላንስ የለዎትም። እባክዎ @Ariff_Support ያናግሩ።", reply_markup=get_main_kb())
        
        admin_text = (
            f"🚨 አዲስ የማስታወቂያ ሙከራ (ባላንስ የለም)\n\n"
            f"👤 ተጠቃሚ: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"💰 የሚፈለግ: {total_price} ብር\n"
            f"📉 ያለው: {balance} ብር"
        )
        try:
            await bot.send_message(ADMIN_ID, admin_text)
        except Exception as e:
            print(f"አድሚን ማሳወቂያ መላክ አልተቻለም: {e}")
        
    conn.close()
    await state.clear()