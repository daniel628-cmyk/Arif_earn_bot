import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import connect_db, init_db

# የHandlers ፋይሎችን ከዚህ አስገባ
from handlers.start import router as start_router
from handlers.channel_handler import router as channel_router
from handlers.bot_handler import router as bot_router  # <--- አዲሱ የቦት ሃንድለር

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Router-ዎችን መመዝገብ
dp.include_router(start_router)
dp.include_router(channel_router)
dp.include_router(bot_router)  # <--- አዲሱን ራውተር እዚህ መመዝገብ አለብህ

async def main():
    # 1. ዳታቤዝ ማገናኘት
    connect_db()
    
    # 2. ሰንጠረዦችን መፍጠር (እዚህ ጋር ነው users, channels እና bots table የሚፈጠሩት)
    init_db()

    print("🚀 Bot is running smoothly...")

    # 3. Conflict እንዳይፈጠር polling መጀመር
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")