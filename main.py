from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# የቦትህን Token እዚህ አስገባ
API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# /start ሲሉ የሚቀበለው ኮድ
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("እንኳን ደህና መጣህ ወደ Arif Earning ቦት! \n\nእንዴት ልረዳህ እችላለሁ?")

# ቦቱን የሚያስጀምር ዋናው ክፍል
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
