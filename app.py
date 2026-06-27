import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import connect_db, init_db

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def echo(msg):
    await msg.answer("Bot is working 🚀")

async def main():
    await connect_db()
    await init_db()

    print("🚀 Bot started")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())