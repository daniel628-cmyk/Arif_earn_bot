import asyncio
import os
from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import connect_db, init_db
from handlers.start import router as start_router

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# register routers
dp.include_router(start_router)

async def main():
    await connect_db()
    await init_db()

    print("🚀 Bot is running")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())