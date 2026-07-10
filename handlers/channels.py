from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from ads_manager import AdsManager

router = Router()

VERIFY_BOT = "YourVerifyBot"   # Example: ArifVerifyBot


@router.message(F.text == "📢 Join Channels")
async def join_channels(message: Message):

    ads = AdsManager.active_channels()

    if not ads:
        return await message.answer(
            "📭 No active channel advertisements."
        )

    for ad in ads:

        ad_id = ad[0]
        owner_id = ad[1]
        channel = ad[2]
        target = ad[3]
        current = ad[4]
        reward = ad[5]

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
                        text="📢 Join Channel",
                        url=f"https://t.me/{channel.replace('@','')}"
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

        remaining = target - current

        await message.answer(

            f"""
📢 <b>Channel Advertisement</b>

🔗 <b>{channel}</b>

💰 Reward: <b>{reward:.2f} Birr</b>

👥 Progress: <b>{current}/{target}</b>

⌛ Remaining: <b>{remaining}</b>

<b>Instructions</b>

1. Join the channel.
2. Click Verify.
3. Verification Bot will check your task.
4. Reward will be added automatically.
""",

            parse_mode="HTML",
            reply_markup=keyboard
        )
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from ads_manager import AdsManager

verify_router = Router()


@verify_router.message(CommandStart())
async def verify_channel(message: Message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return await message.answer(
            "❌ Verification code is missing."
        )

    code = args[1]

    data = AdsManager.verify(code)

    if data is None:
        return await message.answer(
            "❌ Invalid or expired verification code."
        )

    result = AdsManager.complete_campaign(
        user_id=message.from_user.id,
        ad_id=data["ad_id"]
    )

    if not result["success"]:
        return await message.answer(
            result["message"]
        )

    text = (
        "🎉 <b>Task Completed Successfully</b>\n\n"
        f"💰 Reward : <b>{result['reward']:.2f} Birr</b>\n"
        f"👥 Progress : <b>{result['current']}/{result['target']}</b>\n\n"
        "✅ Reward has been added to your Earned Balance."
    )

    await message.answer(
        text,
        parse_mode="HTML"
    )

    if result["completed"]:

        info = AdsManager.campaign_info(
            data["ad_id"]
        )

        if info:

            try:
                await message.bot.send_message(
                    info["owner"],
                    (
                        "🎉 <b>Your advertisement has been completed!</b>\n\n"
                        f"📢 {info['link']}\n"
                        f"👥 {info['target']}/{info['target']}\n\n"
                        "✅ Campaign closed automatically."
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass
from aiogram.exceptions import TelegramBadRequest


async def check_channel_membership(bot, channel_username, user_id):

    try:

        member = await bot.get_chat_member(
            chat_id=channel_username,
            user_id=user_id
        )

        if member.status in (
            "member",
            "administrator",
            "creator",
        ):
            return True

        return False

    except TelegramBadRequest:
        return False

    except Exception:
        return False