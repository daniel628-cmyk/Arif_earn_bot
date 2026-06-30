from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()
    waiting_for_price = State()

@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ ወይም Username ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

@router.message(AdvertiseState.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("👥 ምን ያህል ተጠቃሚዎች (Members) እንዲቀላቀሉ ይፈልጋሉ? (ዝቅተኛው 10)")
    await state.set_state(AdvertiseState.waiting_for_members)

@router.message(AdvertiseState.waiting_for_members)
async def get_members(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 10:
        return await message.answer("❌ እባክዎ ትክክለኛ ቁጥር ይላኩ (ቢያንስ 10 መሆን አለበት)።")
    await state.update_data(members=int(message.text))
    await message.answer("💰 ለአንድ ሰው ምን ያህል መክፈል ይፈልጋሉ? (ለምሳሌ: 0.4)")
    await state.set_state(AdvertiseState.waiting_for_price)

@router.message(AdvertiseState.waiting_for_price)
async def get_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except:
        return await message.answer("❌ እባክዎ ትክክለኛ ቁጥር ይላኩ።")
    
    data = await state.get_data()
    total_price = data['members'] * price
    
    # እዚህ ጋር መረጃውን ወደ ዳታቤዝ ማስገባት ትችላለህ
    await message.answer(
        f"🎉 የቻናል ማስታወቂያ በተሳካ ሁኔታ ተሞልቷል!\n\n"
        f"🔗 Link : {data['link']}\n"
        f"💎 በአንድ ሰው የሚከፈል : {price} ብር\n"
        f"💰 ጠቅላላ ተጠቃሚዎች : {data['members']}\n"
        f"💵 ጠቅላላ ክፍያ: {total_price} ብር"
    )
    await state.clear()