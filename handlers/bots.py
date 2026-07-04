from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ads_manager import AdsManager

router = Router()

@router.message(F.text == "🤖 Join Bots")
async def show_bots(message: Message):
    ads = AdsManager.get_active_ads("bot")
    if not ads:
        return await message.answer("❌ No active bot campaigns.")

    for ad in ads:
        ad_id, owner_id, link, target, current, ad_type = ad
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Open Bot", url=f"https://t.me/{link.replace('@','')}")],
            [InlineKeyboardButton(text="✅ Verify", callback_data=f"vb_{ad_id}")]
        ])
        await message.answer(f"🤖 {link}\nProgress: {current}/{target}", reply_markup=keyboard)