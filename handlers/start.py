from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from db import add_user

router = Router()


def main_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📢 Join Channels"),
                KeyboardButton(text="🤖 Join Bots"),
            ],
            [
                KeyboardButton(text="💰 Balance"),
                KeyboardButton(text="📣 Advertise"),
            ],
            [
                KeyboardButton(text="👥 Referrals"),
                KeyboardButton(text="💸 Withdraw"),
            ],
            [
                KeyboardButton(text="ℹ️ Info"),
            ],
        ],
        resize_keyboard=True
    )


@router.message(CommandStart())
async def start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )

    text = f"""
👋 Welcome, <b>{message.from_user.first_name}</b>

💸 <b>ARIF EARNING BOT</b>

Earn Birr by:

📢 Joining Channels
🤖 Joining Bots
👥 Referring Friends

Choose an option below.
"""

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu()
    )
@router.message(Command("menu"))
async def menu_handler(message: Message):
    await message.answer(
        "🏠 Main Menu",
        reply_markup=get_main_kb()
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        """
📖 <b>How to use Arif Earn Bot</b>

1️⃣ Join Channels
• Complete channel tasks
• Earn Birr

2️⃣ Join Bots
• Start promoted bots
• Earn Birr

3️⃣ Advertise
• Promote your Channel
• Promote your Bot

4️⃣ Withdraw
• Withdraw your earnings

5️⃣ Referrals
• Invite friends
• Earn referral rewards
""",
        parse_mode="HTML",
        reply_markup=get_main_kb()
    )