import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import create_engine, Column, Integer, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. የዳታቤዝ ግንኙነት ከ SSL ድጋፍ ጋር
DATABASE_URL = os.getenv('DATABASE_URL')
# SSL connection ችግርን ለመፍታት connect_args እና pool ቅንብሮች ተጨምረዋል
engine = create_engine(
    DATABASE_URL, 
    connect_args={"sslmode": "require"}, 
    pool_pre_ping=True, 
    pool_recycle=3600
)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 2. የጠረጴዛ መዋቅር
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    balance = Column(Integer, default=0)

Base.metadata.create_all(engine)

# 3. የቦት ማዋቀር
API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# 4. ዋና ሜኑ (Buttons)
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Join Channels", callback_data="join_channels"),
            InlineKeyboardButton(text="🤖 Join Bots", callback_data="join_bots")
        ],
        [InlineKeyboardButton(text="📺 Watch Ads", callback_data="watch_ads")],
        [
            InlineKeyboardButton(text="📤 Withdraw", callback_data="withdraw"),
            InlineKeyboardButton(text="💰 Balance", callback_data="balance")
        ],
        [InlineKeyboardButton(text="ℹ️ Info", callback_data="info")],
        [
            InlineKeyboardButton(text="👥 Referrals", callback_data="referrals"),
            InlineKeyboardButton(text="📈 Advertise", callback_data="advertise")
        ]
    ])
    return keyboard

# 5. የሰላምታ ክፍል
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if not session.query(User).filter_by(telegram_id=user_id).first():
        new_user = User(telegram_id=user_id, balance=0)
        session.add(new_user)
        session.commit()
    
    welcome_text = (
        "🎉 እንኳን ወደ Arif Earning Bot በሰላም መጡ::\n\n"
        "ይህ ቦት ቀላል ስራዎችን በመስራት ብር እንዲያገኙ ይረዳዎታል::\n\n"
        "📢 Join Channels - ቻናሎችን በመቀላቀል ብር ይስሩ\n"
        "🤖 Join Bots - ቦቶችን በመጠቀም ብር ይስሩ\n\n"
        "እንዲሁም የራስዎን ማስታወቂያዎች /advertise ብለው ማስተዋወቅ ይችላሉ::"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu())

# 6. የሂሳብ ማሳያ ክፍል
@dp.callback_query(F.data == "balance")
async def check_balance(callback: types.CallbackQuery):
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    balance = user.balance if user else 0
    await callback.message.answer(f"የእርስዎ ቀሪ ሂሳብ: {balance} ብር ነው::")
    await callback.answer()

# 7. ቦቱን ማስጀመር
async def main():
    # ቦቱ በተመሳሳይ ሰዓት በሌላ ቦታ እንዳይሰራ ለማድረግ 
    # ስልክህ ላይ ያለውን ቦት ሙሉ በሙሉ ማጥፋትህን አረጋግጥ
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
