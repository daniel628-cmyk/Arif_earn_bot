from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

# ዋናው ሜኑ (Buttons)
def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="💰 Balance")],
        [KeyboardButton(text="👥 Referrals"), KeyboardButton(text="📊 Stats")]
    ], resize_keyboard=True)

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    # 1. ተጠቃሚው ተጣብቆበት የነበረውን ስቴት ያጸዳል
    await state.clear() 
    
    # 2. የጠፉትን ሜኑ በተኖች እንደገና ይመልሳል
    await message.answer("ሰላም! ወደ Arif Earning Bot በደህና መጡ።", reply_markup=get_main_kb())