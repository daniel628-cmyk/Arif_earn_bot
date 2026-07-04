from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.exceptions import TelegramBadRequest

from ads_manager import AdsManager

router = Router()


@router.message(F.text == "📢 Join Channels")
async def show_channels(message: Message):

    ads = AdsManager.get_active_ads("channel")

    if not ads:
        await message.answer("❌ No active channel campaigns.")
        return

    for ad in ads:

        ad_id, owner_id, link, target, current, ad_type = ad

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{link.replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify",
                        callback_data=f"verify_channel:{ad_id}:{link}"
                    )
                ]
            ]
        )

        await message.answer(

            f"""
📢 Channel : {link}

👥 Progress : {current}/{target}

💰 Reward : 0.5 Birr
            """,

            reply_markup=keyboard

        )


@router.callback_query(F.data.startswith("verify_channel:"))
async def verify_channel(callback: CallbackQuery, bot: Bot):

    data = callback.data.split(":")

    ad_id = int(data[1])

    username = data[2]

    try:

        member = await bot.get_chat_member(
            chat_id=username,
            user_id=callback.from_user.id
        )

        if member.status not in (
            "member",
            "administrator",
            "creator"
        ):

            await callback.answer(
                "❌ Please join the channel first.",
                show_alert=True
            )
            return

    except TelegramBadRequest:

        await callback.answer(
            "❌ Bot is not admin in this channel.",
            show_alert=True
        )
        return

    result = AdsManager.update_ad_progress(
        ad_id,
        callback.from_user.id
    )

    if result["success"]:

        if result.get("completed"):

            try:

                await callback.message.edit_text(
                    "✅ Campaign Completed."
                )

            except:

                pass

        await callback.answer(
            result["message"],
            show_alert=True
        )

    else:

        await callback.answer(
            result["message"],
            show_alert=True
        )