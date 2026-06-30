from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db import add_user
from keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):

    user_id = message.from_user.id
    username = message.from_user.username or ""

    add_user(user_id, username)

    text = f"""
👋 Welcome {message.from_user.first_name}

💰 Earn money by completing simple tasks.

Choose one of the options below.
"""

    await message.answer(
        text,
        reply_markup=main_menu
    )