from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from database import get_db, mark_bot_as_done

router = Router()


@router.message(F.text == "🤖 Join Bots")
async def join_bots_handler(message: Message):
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, bot_username, bot_name
            FROM bots
            WHERE is_active = TRUE
        """)
        bots = cur.fetchall()

    conn.close()

    if not bots:
        await message.answer("📭 አሁን ምንም Bot Task የለም።")
        return

    for bot_id, username, name in bots:

        kb = InlineKeyboardMarkup(
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
                        callback_data=f"verify_bot:{bot_id}:{username}"
                    )
                ]
            ]
        )

        await message.answer(
            f"🤖 {name}\n\n"
            f"1. Open Bot\n"
            f"2. Press /start\n"
            f"3. Return and Verify",
            reply_markup=kb
        )


@router.callback_query(F.data.startswith("verify_bot:"))
async def verify_bot(callback: CallbackQuery, bot: Bot):

    _, bot_id, username = callback.data.split(":")

    user_id = callback.from_user.id

    try:
        member = await bot.get_chat_member(f"@{username}", user_id)

        if member.status == "left":
            await callback.answer(
                "❌ መጀመሪያ Bot-ን Start ያድርጉ!",
                show_alert=True
            )
            return

    except TelegramBadRequest:
        await callback.answer(
            "❌ Bot አልተገኘም!",
            show_alert=True
        )
        return

    if mark_bot_as_done(user_id, int(bot_id)):
        await callback.answer(
            "✅ 50 ብር ተጨምሯል!",
            show_alert=True
        )
    else:
        await callback.answer(
            "⚠️ ቀድሞ ሰርተውታል!",
            show_alert=True
        )