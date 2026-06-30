# handlers/channels.py
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from db import get_db
from utils.checks import check_user_sub

router = Router()

@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    channel_db_id = int(callback.data.split("_")[1])
    
    # 1. ከዳታቤዝ የቻናሉን ID አምጣ
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT channel_id FROM channels WHERE id = %s", (channel_db_id,))
    res = cur.fetchone()
    conn.close()
    
    if not res:
        await callback.answer("ቻናሉ አልተገኘም!", show_alert=True)
        return
    
    chat_id = res[0]
    
    # 2. ተጠቃሚው መቀላቀሉን ቼክ አድርግ
    is_joined = await check_user_sub(bot, chat_id, callback.from_user.id)
    
    if is_joined:
        # እዚህ ጋር ለተጠቃሚው ነጥብ የምትጨምርበትን ኮድ አስገባ (ለምሳሌ balance update)
        await callback.answer("✅ ተረጋግጧል! ሽልማት ተሰጥቶዎታል!", show_alert=True)
    else:
        await callback.answer("❌ ገና አልተቀላቀሉም! እባክዎ ይቀላቀሉ!", show_alert=True)