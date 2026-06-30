from aiogram import Router, F
from aiogram.types import Message

# ይህ መስመር የግድ መኖር አለበት!
router = Router() 

# ከዚህ በታች ያሉትን የ Handler ኮዶችህን በ router.message ወይም router.callback_query መልክ ጻፋቸው።
@router.message(F.text == "💸 Withdraw")
async def withdraw_handler(message: Message):
    # የ Withdraw ኮድህ እዚህ...
    await message.answer("የሚወጣው ገንዘብ መጠን...")