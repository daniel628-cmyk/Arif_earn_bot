from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext # ይሄንን አስገባ

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext): # state ፓራሜትር ጨምር
    await state.clear() # ተጠቃሚው ተጣብቆበት የነበረውን ስቴት አጽዳ
    await message.answer("ሰላም! ወደ Arif Earning Bot በደህና መጡ። ምን ማድረግ ይፈልጋሉ?")