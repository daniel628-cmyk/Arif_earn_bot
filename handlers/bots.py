from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from ads_manager import AdsManager

router = Router()

BOT_USERNAME = "YourBotUsername"   # Example: MyTaskBot


@router.message(F.text == "🤖 Join Bots")
async def join_bots(message: Message):

    ads = AdsManager.active_bots()

    if not ads:
        return await message.answer(
            "❌ No active bot campaigns."
        )

    for ad in ads:

        ad_id = ad[0]
        owner_id = ad[1]
        bot_username = ad[2]
        target = ad[3]
        current = ad[4]
        reward = ad[5]

        code = AdsManager.generate_code(
            message.from_user.id,
            ad_id
        )

        verify_url = (
            f"https://t.me/{BOT_USERNAME}"
            f"?start={code}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Open Bot",
                        url=f"https://t.me/{bot_username.replace('@','')}"
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
🤖 <b>Bot Advertisement</b>

🔗 <b>{bot_username}</b>

💰 Reward: <b>{reward:.2f} Birr</b>

👥 Progress: <b>{current}/{target}</b>

⌛ Remaining: <b>{remaining}</b>

<b>Instructions</b>

1. Open the bot.
2. Press /start.
3. Return and press Verify.
4. If verified, your reward will be added automatically.
""",
            parse_mode="HTML",
            reply_markup=keyboard
        )
from aiogram.filters import CommandStart
from aiogram.types import Message


@router.message(CommandStart())
async def verify_bot(message: Message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        return await message.answer(
            "❌ Verification code not found."
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

    await message.answer(

        f"""
🎉 <b>Verification Successful</b>

💰 Reward: <b>{result['reward']:.2f} Birr</b>

👥 Progress: <b>{result['current']}/{result['target']}</b>

✅ {result['message']}
""",

        parse_mode="HTML"

    )

    if result["completed"]:

        info = AdsManager.campaign_info(
            data["ad_id"]
        )

        if info:

            try:

                await message.bot.send_message(

                    chat_id=info["owner"],

                    text=f"""
🎉 <b>Campaign Completed</b>

📢 {info['link']}

👥 {info['target']}/{info['target']}

✅ Your advertisement has finished successfully.
""",

                    parse_mode="HTML"

                )

            except Exception:
                pass
