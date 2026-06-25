import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# ቶከኑን ከ Railway Variables ይወስዳል
TOKEN = os.getenv('API_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("እንኳን ደህና መጣህ ወደ Arif Earning ቦት!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
