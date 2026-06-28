from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_db, mark_bot_as_done

router = Router()

@router.message(F.text == "🤖 Join Bots")
async def join_bots_handler(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, bot_username, bot_name FROM bots WHERE is_active = TRUE")
        bots = cur.fetchall()
    conn.close()
            
    if not bots:
        await message.answer("በአሁኑ ሰዓት ምንም ቦት የለም።")
        return

    for b_id, username, name in bots:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ወደ ቦቱ ሂድ", url=f"https://t.me/{username}")],
            [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vb_{b_id}")]
        ])
        await message.answer(f"ቦት፡ {name}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("vb_"))
async def verify_bot_callback(callback: CallbackQuery):
    bot_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    if mark_bot_as_done(user_id, bot_id):
        await callback.answer("✅ ተሳክቷል! 50 ብር ተጨምሮልዎታል!", show_alert=True)
    else:
        await callback.answer("⚠️ ቀድመው ሰርተውታል!", show_alert=True)