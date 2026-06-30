from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import get_bots, mark_bot_done

router = Router()


@router.message(F.text == "🤖 Join Bots")
async def join_bots(message: Message):

    bots = get_bots()

    if not bots:
        await message.answer("❌ No bots available.")
        return

    for bot_id, username, name in bots:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Open Bot",
                        url=f"https://t.me/{username}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify",
                        callback_data=f"verify_bot:{bot_id}"
                    )
                ]
            ]
        )

        await message.answer(
            f"🤖 {name}",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("verify_bot:"))
async def verify(callback: CallbackQuery):

    bot_id = int(callback.data.split(":")[1])

    success = mark_bot_done(
        callback.from_user.id,
        bot_id
    )

    if success:

        await callback.answer(
            "✅ 0.25 Birr Added!",
            show_alert=True
        )

    else:

        await callback.answer(
            "⚠ Already completed.",
            show_alert=True
        )