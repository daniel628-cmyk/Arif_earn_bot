from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_db, add_balance

router = Router()


@router.callback_query(F.data == "join_channels")
async def join_channels(callback: CallbackQuery):

    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id,
                   channel_name,
                   channel_username,
                   reward
            FROM channels
            WHERE is_active = TRUE
        """)

        channels = cur.fetchall()

    conn.close()

    if not channels:
        await callback.message.answer("📢 No channels available.")
        await callback.answer()
        return

    for channel_id, name, username, reward in channels:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{username}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify",
                        callback_data=f"verify_channel_{channel_id}"
                    )
                ]
            ]
        )

        await callback.message.answer(
            f"""
📢 {name}

💰 Reward : {reward} Birr
""",
            reply_markup=keyboard
        )

    await callback.answer()