import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ከ Railway Variables ቶከኑን ይወስዳል
TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

# የታችኛው ሜኑ አዝራሮች (Reply Keyboard)
def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots"), KeyboardButton(text="📺 Watch Ads")],
            [KeyboardButton(text="💸 Withdraw"), KeyboardButton(text="💰 Balance"), KeyboardButton(text="ℹ️ Info")],
            [KeyboardButton(text="👥 Referrals"), KeyboardButton(text="📢 Advertise")]
        ],
        resize_keyboard=True
    )
    return keyboard

# /start ሲሉ የሚሰጠው ምላሽ
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    welcome_text = (
        "🎉 እንኳን ወደ Arif Earning Bot በሰላም መጡ::\n\n"
        "ይህ ቦት ቀላል ስራዎችን በመስራት ብር እንዲያገኙ ያስችልዎታል::\n\n"
        "📢 Join Channels - ቻናሎችን በመቀላቀል ብር ይስሩ\n"
        "🤖 Join Bots - ቦቶችን በመቀላቀል ብር ይስሩ\n\n"
        "እንዲሁም የራስዎን ማስታወቂያዎች /advertise ብለው ማስተዋወቅ ይችላሉ::"
    )
    await message.answer(welcome_text, reply_markup=main_menu())

# አዝራሮቹ ሲጫኑ የሚሰጡ ምላሾች (ለምሳሌ)
@dp.message(F.text == "💰 Balance")
async def balance_handler(message: types.Message):
    await message.answer("የእርስዎ አሁን ያለው ሂሳብ 0 ብር ነው።")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
