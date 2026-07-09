from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from ads_manager import AdsManager

router = Router()

VERIFY_BOT = "YourVerifyBot"   # @YourVerifyBot


@router.message(F.text == "🤖 Join Bots")
async def join_bots(message: Message):

    ads = AdsManager.active_bots()

    if not ads:
        return await message.answer(
            "📭 No active bot advertisements."
        )

    for ad in ads:

        ad_id = ad[0]
        link = ad[2]
        target = ad[3]
        current = ad[4]

        code = AdsManager.generate_code(
            message.from_user.id,
            ad_id
        )

        verify_url = (
            f"https://t.me/{VERIFY_BOT}"
            f"?start={code}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Start Bot",
                        url=f"https://t.me/{link.replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify",
                        url=verify_url
                    )
                ]
            ]
        )

        remain = target - current

        text = (
            "🤖 <b>Bot Advertisement</b>\n\n"

            f"🔗 {link}\n\n"

            f"💰 Reward : <b>0.27 Birr</b>\n"

            f"👥 Progress : <b>{current}/{target}</b>\n"

            f"⌛ Remaining : <b>{remain}</b>\n\n"

            "1️⃣ Click Start Bot.\n"
            "2️⃣ Press START in the advertised bot.\n"
            "3️⃣ Return and press Verify.\n"
            "4️⃣ Verification Bot will reward you."
        )

        await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )