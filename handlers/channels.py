from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_db
# ከዚህ በፊት የነበሩትን import-ዎችህን በዚህ አስገባ
from utils.checks import check_user_sub 

# 1. ይሄ መስመር የግድ ያስፈልጋል!
router = Router()

# 2. አሁን router ተብሎ ስለተገለጸ ከታች ያሉት ኮዶች ይሰራሉ
@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        # አሁን ከ ads table ነው መረጃውን የምንስበው
        cur.execute("SELECT id, link FROM ads WHERE type = 'channel' AND status = 'active'")
        ads = cur.fetchall()
    conn.close()

    if not ads:
        return await message.answer("❌ በአሁኑ ሰዓት የሚገኙ ቻናሎች የሉም።")

    for ad_id, link in ads:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 ወደ ቻናሉ ሂድ", url=f"https://t.me/{link.replace('@', '')}")],
            [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vc_{ad_id}")]
        ])
        await message.answer(f"📢 ቻናል:🎯 ተልዕኮ:- ቻነሉን ይቀላቀሉ፤ እንዲሁም ንቁ ተሳታፊ ይሁኑ።


==================
❓ ከተቀላቀሉ በኋላ «✅ አድርጊያለሁ»ን ይጫኑ። {link}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    ad_id = int(callback.data.split("_")[1])
    
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT link FROM ads WHERE id = %s", (ad_id,))
        res = cur.fetchone()
    conn.close()
    
    if not res:
        return await callback.answer("❌ ማስታወቂያው አልተገኘም።", show_alert=True)
    
    channel_link = res[0]
    
    # ቻናሉን መፈተሽ
    if await check_user_sub(bot, channel_link, callback.from_user.id):
        await callback.answer("✅ ተረጋግጧል! ሽልማት ተሰጥቶዎታል!", show_alert=True)
    else:
        await callback.answer("❌ ገና አልተቀላቀሉም!", show_alert=True)