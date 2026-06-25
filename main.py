import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from sqlalchemy import create_engine, Column, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. የዳታቤዝ ግንኙነት (ከ Railway Variables የሚወሰድ)
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 2. የጠረጴዛ መዋቅር (Table Schema)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    balance = Column(Integer, default=0)

Base.metadata.create_all(engine)

# 3. ቦቱን ማዋቀር
API_TOKEN = os.getenv('BOT_TOKEN') # በRailway ላይ ታስገባዋለህ
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 4. ትዕዛዞች
@dp.message(Command("start"))
async def start(message: types.Message):
    # ተጠቃሚን መመዝገብ
    user_id = message.from_user.id
    if not session.query(User).filter_by(telegram_id=user_id).first():
        new_user = User(telegram_id=user_id, balance=0)
        session.add(new_user)
        session.commit()
    
    await message.answer("እንኳን ወደ ቦቱ በደህና መጡ! ሂሳብዎን ለማየት /balance ይጫኑ።")

@dp.message(Command("balance"))
async def get_balance(message: types.Message):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    await message.answer(f"የእርስዎ ቀሪ ሂሳብ: {user.balance} ብር ነው::")

# 5. ቦቱን ማስጀመር
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
