from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_menu import main_menu

router = Router()

@router.message(CommandStart())
async def start(message: Message):

    text = """
👋 <b>Welcome to Arif Earning Bot</b>

💸 Earn money by completing tasks.

Choose one of the options below.
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu
    )