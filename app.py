import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from db import connect_db, init_db

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.channels import router as channels_router
from handlers.bots import router as bots_router
from handlers.balance import router as balance_router
from handlers.withdraw import router as withdraw_router
from handlers.referrals import router as referrals_router
from handlers.advertise import router as advertise_router
from handlers.info import router as info_router
from handlers.admin import router as admin_router


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.include_router(start_router)
dp.include_router(menu_router)
dp.include_router(channels_router)
dp.include_router(bots_router)
dp.include_router(balance_router)
dp.include_router(withdraw_router)
dp.include_router(referrals_router)
dp.include_router(advertise_router)
dp.include_router(info_router)
dp.include_router(admin_router)


async def main():
    connect_db()
    init_db()

    print("✅ Bot Started Successfully")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())