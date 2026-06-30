from aiogram import Router, F
from aiogram.types import Message

# ይህ መስመር በጣም ወሳኝ ነው!
router = Router() 

# ከዚህ በታች ያሉትን handler-ዎችህን በ router.message ወይም router.callback_query መልክ ጻፋቸው
# ለምሳሌ፡
@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    # የባላንስ ኮድህ እዚህ ይገባል
    await message.answer("የእርስዎ ባላንስ፡ 0 ነው")