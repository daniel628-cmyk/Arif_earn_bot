from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db

router = Router()

@router.message(F.text == "📢 Join Channels")
async def join_channels_handler(message: Message):
    # ከዳታቤዝ ቻናሎችን ማምጣት
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT channel_link, channel_name FROM channels WHERE is_active = TRUE")
    channels = cur.fetchall()
    cur.close()

    if not channels:
        await message.answer("በአሁኑ ሰዓት ምንም ቻናል የለም።")
        return

    # ቻናሎችን በ Inline Buttons ማሳየት
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, url=link)] for link, name in channels
    ])
    
    await message.answer("ለማግኘት ከታች ያሉትን ቻናሎች ይቀላቀሉ፡", reply_markup=keyboard)