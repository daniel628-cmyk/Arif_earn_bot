from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from db import get_db, update_and_check_limit

router = Router()

# 1. ተጠቃሚው "Join Bots" የሚለውን ቁልፍ ሲጫን
@router.message(F.text == "🤖 Join Bots")
async def show_bots(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, bot_name, bot_username FROM bots WHERE is_active = TRUE")
        bots = cur.fetchall()
    conn.close()

    if not bots:
        await message.answer("በአሁኑ ሰዓት ምንም ቦት የለም።")
        return

    for b_id, name, username in bots:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ወደ ቦቱ ሂድ", url=f"https://t.me/{username}")],
            [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vb_{b_id}")]
        ])
        await message.answer(f"ቦት፡ {name}", reply_markup=keyboard)

# 2. የVerify ሎጂክ (ለቦቶች)
@router.callback_query(F.data.startswith("vb_"))
async def verify_bot_callback(callback: CallbackQuery):
    bot_db_id = int(callback.data.split("_")[1])
    
    # የቦት ማረጋገጫ (Bot-to-Bot verification አስቸጋሪ ስለሆነ 
    # ብዙውን ጊዜ የVerify ቁልፉን ሲጫን እንደተቀላቀለ ይቆጠራል)
    update_and_check_limit("bots", bot_db_id)
    await callback.answer("✅ ተረጋግጧል! ሽልማት ተሰጥቶዎታል!", show_alert=True)