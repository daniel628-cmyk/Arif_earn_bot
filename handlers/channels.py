from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from ads_manager import AdsManager

router = Router()

@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):
    ads = AdsManager.get_active_ads(ad_type="channel")
    
    if not ads:
        return await message.answer("❌ No active channel campaigns at the moment.")

    for ad in ads:
        ad_id, link, target, current, price, ad_type = ad
        remaining = target - current
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{link.replace('@', '')}")],
            [InlineKeyboardButton(text="✅ Verify", callback_data=f"vc_{ad_id}")]
        ])
        
        await message.answer(
            f"📢 Channel: {link}\n"
            f"👥 Progress: {current}/{target} people\n"
            f"⏳ Remaining: **{remaining}** spots\n"
            f"💰 Reward: 0.30 Birr",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("vc_"))
async def verify_channel_callback(callback: CallbackQuery, bot: Bot):
    ad_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    result = AdsManager.update_ad_progress(ad_id, user_id)

    if result["success"]:
        await callback.answer(result["message"], show_alert=True)
        
        # Update message if campaign is completed
        if result.get("completed"):
            try:
                await callback.message.edit_text(
                    "🎉 This campaign has reached its target and is now closed."
                )
            except:
                pass
    else:
        await callback.answer(result["message"], show_alert=True)