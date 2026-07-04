from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text == "ℹ️ Info")
async def info(message: Message):
    await message.answer(
        "ℹ️ **Arif Earn Bot Info**\n\n"
        "• Earn by joining channels & bots\n"
        "• 0.5 Birr per task\n"
        "• Refer friends for rewards\n"
        "• Minimum withdrawal: 25 Birr\n\n"
        "Contact Admin: @Ariff_Support"
    )