from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_db
from utils.checks import check_user_sub

# ይህ መስመር የግድ መኖር አለበት!
router = Router()

@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        # ገባሪ የሆኑ ማስታወቂያዎችን ከ ads table አምጣ
        cur.execute("SELECT id, link FROM ads WHERE type = 'channel' AND status = 'active'")
        ads = cur.fetchall()
    conn.close()

    if not ads:
        return await message.answer("❌ በአሁኑ ሰዓት ምንም የሚገኙ ቻናሎች የሉም።")

    for ad_id, link in ads:
        # ለየቻናሉ Verify button ይፍጠር
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 ወደ ቻናሉ ሂድ", url=f"https://t.me/{link.replace('@', '')}")],
            [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vc_{ad_id}")]
        ])
        await message.answer(f"📢 ቻናል: {link}", reply_markup=keyboard)

@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    ad_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        # 1. ተጠቃሚው ቀድሞ ሰርቶት እንደሆነ ፈትሽ
        cur.execute("SELECT 1 FROM completed_ads WHERE user_id = %s AND ad_id = %s", (user_id, ad_id))
        if cur.fetchone():
            await callback.answer("❌ ይህንን ማስታወቂያ ቀድመው ሰርተውታል!", show_alert=True)
            conn.close()
            return

        # 2. የቻናል ሊንኩን አምጣ
        cur.execute("SELECT link FROM ads WHERE id = %s", (ad_id,))
        res = cur.fetchone()
        
        if not res:
            await callback.answer("❌ ማስታወቂያው ጊዜው አልፎበታል!", show_alert=True)
            conn.close()
            return

        channel_link = res[0]

        # 3. ቻናል መቀላቀሉን አረጋግጥ
        if await check_user_sub(bot, channel_link, user_id):
            # ባላንስ መጨመር
            cur.execute("UPDATE balances SET amount = amount + 0.30 WHERE user_id = %s", (user_id,))
            # ተጠናቀቀ ብሎ መዝገብ
            cur.execute("INSERT INTO completed_ads (user_id, ad_id) VALUES (%s, %s)", (user_id, ad_id))
            conn.commit()
            await callback.answer("✅ ተረጋግጧል! 0.30 ብር ወደ ባላንስዎ ተጨምሯል!", show_alert=True)
        else:
            await callback.answer("❌ ገና አልተቀላቀሉም!", show_alert=True)
    conn.close()