from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from ads_manager import AdsManager

router = Router()

@router.message(F.text == "🤖 Join Bots")
async def show_bots(message: Message):
    ads = AdsManager.get_active_ads(ad_type="bot")
    
    if not ads:
        return await message.answer("❌ No active bot campaigns at the moment.")

    for ad in ads:
        ad_id, link, target, current, price, ad_type = ad
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Start Bot", url=f"https://t.me/{link.replace('@', '')}")],
            [InlineKeyboardButton(text="✅ Verify", callback_data=f"vb_{ad_id}")]
        ])
        
        await message.answer(
            f"🤖 Bot: {link}\n"
            f"Progress: {current}/{target} people", 
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("vb_"))
async def verify_bot_callback(callback: CallbackQuery, bot: Bot):
    ad_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    result = AdsManager.update_ad_progress(ad_id, user_id)

    if result["success"]:
        await callback.answer(result["message"], show_alert=True)
        
        if result.get("completed"):
            try:
                await callback.message.edit_text(
                    "🎉 This bot campaign has reached its target and is now closed."
                )
            except:
                pass
    else:
        await callback.answer(result["message"], show_alert=True)