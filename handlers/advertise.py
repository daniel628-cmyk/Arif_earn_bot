
from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID, BOT_USERNAME

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()
    waiting_for_bot_msg = State() # ለቦት ማስታወቂያ

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
        await call.message.answer("🔗 ቻናሉ ላይ Bot Admin ያድርጉ። ከዛ ቻናል ሊንክ (ለምሳሌ @የቻናል ሊንክ ) ይላኩ።")
        await state.set_state(AdvertiseState.waiting_for_link)
    else:
        await call.message.answer("🔎 ማስተዋወቅ የሚፈልጉትን የቦት Message Forward ያድርጉ:")
        await state.set_state(AdvertiseState.waiting_for_bot_msg)
    await call.answer()

# ቻናል ማረጋገጫ እና ሌሎች ሂደቶች እዚህ ይገባሉ...
# (ከዚህ ቀደም የሰራነው የአድሚንነት ማረጋገጫ ሎጂክ እዚህ ይጨመራል)

@router.message(F.text == "📊 My Ads")
async def show_my_ads(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM ads WHERE user_id = %s", (message.from_user.id,))
        ads = cur.fetchall()
    conn.close()
    
    if not ads:
        return await message.answer("❌ እስካሁን ምንም ማስታወቂያ የለዎትም።")
    
    for ad in ads:
        # ad[0]=id, ad[2]=link, ad[3]=target, ad[4]=current, ad[5]=price, ad[6]=status
        msg = (f"📊 የማስታወቂያ ሁኔታ\n\n🆔 Task ID: {ad[0]}\n🔗 Link: {ad[2]}\n"
               f"👥 Remaining: {ad[3]-ad[4]}/{ad[3]}\n✅ Completed: {ad[4]}\n"
               f"💵 Spent: {ad[4] * 0.5} Birr")
        await message.answer(msg)