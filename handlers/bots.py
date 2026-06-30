from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from db import get_db

router = Router()


@router.message(F.text == "🤖 Join Bots")
async def join_bots(message: Message):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, bot_username, bot_name
        FROM bots
        WHERE is_active=TRUE
    """)

    bots = cur.fetchall()

    cur.close()
    conn.close()

    if not bots:
        await message.answer("❌ No bots available.")
        return

    for bot in bots:

        bot_id = bot[0]
        username = bot[1]
        name = bot[2]