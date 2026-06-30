from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db

router = Router()  # ይህ መስመር የግድ መኖር አለበት!

# የማስታወቂያ ግብዓቶች (States)
class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_amount = State()

@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ወይም የቦት ሊንክ ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)