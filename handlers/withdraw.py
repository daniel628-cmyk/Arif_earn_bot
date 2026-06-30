from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db

ADMIN_ID = 123456789  # እዚህ የራስህን Telegram ID አስገባ
router = Router()

class WithdrawForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_amount = State()

@router.message(F.text == "💸 Withdraw")
async def start_withdraw(message: Message, state: FSMContext):
    # ባላንሱን ይመልከቱ
    user_id = message.from_user.id
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        res = cur.fetchone()
        amount = res[0] if res else 0
    conn.close()

    if amount < 50:
        await message.answer(f"❌ ቢያንስ 50 ብር ሊኖርዎት ይገባል። የእርስዎ ባላንስ፡ {amount} ብር ነው።")
    else:
        await message.answer("✅ እባክዎን የቴሌብር ስምዎን (Full Name) ይላኩ።")
        await state.set_state(WithdrawForm.waiting_for_name)

@router.message(WithdrawForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("✅ የቴሌብር ስልክ ቁጥርዎን ይላኩ።")
    await state.set_state(WithdrawForm.waiting_for_phone)

@router.message(WithdrawForm.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("✅ ማውጣት የሚፈልጉትን የገንዘብ መጠን ይላኩ።")
    await state.set_state(WithdrawForm.waiting_for_amount)

@router.message(WithdrawForm.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext, bot):
    user_data = await state.get_data()
    amount = message.text
    
    # ለአድሚን መላክ
    await bot.send_message(
        ADMIN_ID, 
        f"💸 **አዲስ የWithdraw ጥያቄ!**\n\n"
        f"👤 ተጠቃሚ፡ @{message.from_user.username or 'N/A'}\n"
        f"📛 ስም፡ {user_data['name']}\n"
        f"📱 ስልክ፡ {user_data['phone']}\n"
        f"💰 መጠን፡ {amount} ብር"
    )
    
    await message.answer("✅ ጥያቄዎ በተሳካ ሁኔታ ለአድሚን ተልኳል። በቅርቡ ክፍያ ይፈጸምልዎታል!")
    await state.clear()