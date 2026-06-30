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
@router.callback_query(F.data.startswith("verify_channel_"))
async def verify_channel(callback: CallbackQuery):

    channel_id = int(callback.data.split("_")[2])

    user_id = callback.from_user.id

    conn = get_db()

    with conn.cursor() as cur:

        cur.execute("""
        SELECT 1
        FROM user_channel_tasks
        WHERE user_id=%s
        AND channel_id=%s
        """,
        (user_id, channel_id))

        if cur.fetchone():

            await callback.answer(
                "✅ Already completed.",
                show_alert=True
            )

            conn.close()
            return

        cur.execute("""
        SELECT reward
        FROM channels
        WHERE id=%s
        """,
        (channel_id,))

        reward = cur.fetchone()[0]

        cur.execute("""
        INSERT INTO user_channel_tasks(
            user_id,
            channel_id
        )
        VALUES(%s,%s)
        """,
        (user_id, channel_id))

    conn.commit()
    conn.close()

    add_balance(user_id, reward)

    await callback.answer(
        f"🎉 {reward} Birr Added.",
        show_alert=True
    )