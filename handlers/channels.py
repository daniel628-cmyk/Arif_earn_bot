from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_db, update_and_check_limit
from utils.checks import check_user_sub

router = Router()

# 1. አዲሱ Handler: ተጠቃሚው button-ውን ሲጫን
@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        # ገባሪ የሆኑትን ብቻ አምጣ
        cur.execute("SELECT id, channel_link, channel_name FROM channels WHERE is_active = TRUE")
        channels = cur.fetchall()
    conn.close()

    if not channels:
        await message.answer("በአሁኑ ሰዓት ምንም ቻናል የለም።")
        return

    for c_id, link, name in channels:
        # ለየቻናሉ Verify button ይፍጠር
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="ወደ ቻናሉ ሂድ", url=link)],
            [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vc_{c_id}")]
        ])
        await message.answer(f"ቻናል፡ {name}", reply_markup=keyboard)

# 2. የድሮው Handler: ተጠቃሚው Verify button-ውን ሲጫን
@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    channel_db_id = int(callback.data.split("_")[1])
    
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT channel_id FROM channels WHERE id = %s", (channel_db_id,))
        res = cur.fetchone()
    conn.close()
    
    if not res:
        await callback.answer("ቻናሉ አልተገኘም!", show_alert=True)
        return
    
    chat_id = res[0]
    
    if await check_user_sub(bot, chat_id, callback.from_user.id):
        update_and_check_limit("channels", channel_db_id)
        await callback.answer("✅ ተረጋግጧል! ሽልማት ተሰጥቶዎታል!", show_alert=True)
    else:
        await callback.answer("❌ ገና አልተቀላቀሉም!", show_alert=True)