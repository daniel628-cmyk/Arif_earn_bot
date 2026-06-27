from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_pool

router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message):

    pool = await get_pool()

    user_id = message.from_user.id
    username = message.from_user.username

    await pool.execute("""
        INSERT INTO users (user_id, username, balance)
        VALUES ($1, $2, 0)
        ON CONFLICT (user_id) DO NOTHING
    """, user_id, username)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Balance", callback_data="balance")],
        [InlineKeyboardButton(text="📢 Advertising", callback_data="ads")],
        [InlineKeyboardButton(text="📊 Tasks", callback_data="tasks")]
    ])

    await message.answer(
        "👋 Welcome to Ads Bot!\nChoose option below:",
        reply_markup=keyboard
    )