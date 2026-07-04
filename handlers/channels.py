from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ads_manager import AdsManager

router = Router()

@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):
    ads = AdsManager.get_active_ads(ad_type="channel")
    
    if not ads:
        return await message.answer("❌ No active channel campaigns right now.")

    for ad in ads:
        ad_id, user_id, link, target, current, ad_type = ad
        remaining = target - current

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Join Channel", url=f"https://t.me/{link.replace('@','')}")],
            [InlineKeyboardButton(text="✅ Verify", callback_data=f"vc_{ad_id}")]
        ])

        await message.answer(
            f"📢 Channel: {link}\n"
            f"👥 Progress: {current}/{target}\n"
            f"⏳ Remaining: {remaining} spots\n"
            f"💰 Reward: 0.5 Birr",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("vc_"))
async def verify_channel(callback: CallbackQuery, bot: Bot):
    ad_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id

    # Call the manager
    result = AdsManager.update_ad_progress(ad_id, user_id)

    if result["success"]:
        await callback.answer(result["message"], show_alert=True)

        if result.get("completed"):
            try:
                await callback.message.edit_text("🎉 This campaign is now completed!")
            except:
                pass
    else:
        await callback.answer(result["message"], show_alert=True)