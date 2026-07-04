from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from ads_manager import AdsManager

router = Router()


@router.message(F.text == "🤖 Join Bots")
async def show_bots(message: Message):

    ads = AdsManager.get_active_ads("bot")

    if not ads:
        await message.answer("❌ No active bot advertisements.")
        return

    for ad in ads:

        ad_id, owner_id, bot_username, target, current, ad_type = ad

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Open Bot",
                        url=f"https://t.me/{bot_username.replace('@','')}?start=ad_{ad_id}_{message.from_user.id}"
                    )
                ]
            ]
        )

        remain = target - current

        await message.answer(

            f"""
🤖 Bot Advertisement

Bot : {bot_username}

👥 Progress : {current}/{target}

📌 Remaining : {remain}

💰 Reward : 0.30 Birr
""",

            reply_markup=keyboard

        )