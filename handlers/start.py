from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # ማንኛውንም የተጣበቀ ስቴት ያጸዳል
    await state.clear() 
    await message.answer(
        "ሰላም! ወደ Arif Earning Bot በደህና መጡ።\n\n"
        "ከታች ካሉት አማራጮች ውስጥ የሚፈልጉትን ይምረጡ:", 
        reply_markup=get_main_kb()
    )