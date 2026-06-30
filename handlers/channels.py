# handlers/channels.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from db import get_db, update_and_check_limit
from utils.checks import check_user_sub

router = Router()

@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    channel_db_id = int(callback.data.split("_")[1])
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT channel_id FROM channels WHERE id = %s", (channel_db_id,))
    res = cur.fetchone()
    conn.close()
    
    if not res:
        await callback.answer("ቻናሉ አልተገኘም!", show_alert=True)
        return
    
    chat_id = res[0]
    
    # ቻናሉን ቼክ አድርግ
    if await check_user_sub(bot, chat_id, callback.from_user.id):
        # 1. ሽልማት ስጠው (እዚህ balance update ኮድህን ጨምር)
        # 2. ገደብ መድረሱን እና ብዛቱን አዘምን
        update_and_check_limit("channels", channel_db_id)
        await callback.answer("✅ ተረጋግጧል! ሽልማት ተሰጥቶዎታል!", show_alert=True)
    else:
        await callback.answer("❌ ገና አልተቀላቀሉም!", show_alert=True)