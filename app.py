import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import connect_db, init_db

# የHandlers ፋይሎች
from handlers.start import router as start_router
from handlers.channel_handler import router as channel_router
from handlers.bot_handler import router as bot_router # አዲሱ Handler

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Router-ዎችን መመዝገብ
dp.include_router(start_router)
dp.include_router(channel_router)
dp.include_router(bot_router) # አዲሱን ራውተር አስገባ

async def main():
    connect_db()
    init_db()
    print("🚀 Bot is running smoothly...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())