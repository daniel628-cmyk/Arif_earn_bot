from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import add_user

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    add_user(user_id, username, first_name)

    await message.answer(
        "👋 Welcome to **Arif Earn Bot**!\n\n"
        "Earn money by joining channels, bots, and referring friends.\n"
        "Use the menu below:",
        reply_markup=get_main_kb()
    )

def get_main_kb():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)