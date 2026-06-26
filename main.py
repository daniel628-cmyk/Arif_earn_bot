import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from supabase import create_client

# 1. Configuration (ከRailway Variables የሚወስድ)
API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 2. Initialize Clients
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. /start handler
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "No_Username"
    
    try:
        # ተጠቃሚውን በ 'users' ጠረጴዛ ውስጥ ይመዘግባል
        user_data = {
            "user_id": user_id,
            "username": username,
            "balance": 0.0
        }
        
        # Upsert: ተጠቃሚው ካለ ያዘምናል፣ ከሌለ ይፈጥራል
        supabase.table("users").upsert(user_data).execute()
        
        # የዌልካም መልእክት
        welcome_text = (
            f"እንኳን በደህና መጡ! 🌟 {message.from_user.first_name}\n\n"
            "ወደ 'Arif Earn Bot' በሰላም መጡ። እዚህ ቦት ውስጥ የተለያዩ ስራዎችን በመስራት ገንዘብ ማግኘት ይችላሉ።\n\n"
            "✅ ከታች ያሉትን አማራጮች በመጠቀም ስራዎችን መጀመር ይችላሉ፦\n"
            "💰 ሂሳብዎን ለመመልከት /balance ይጫኑ።\n"
            "📋 ስራዎችን ለመስራት /tasks ይጫኑ።\n\n"
            "ስለተቀላቀሉን እናመሰግናለን!"
        )
        
        await message.answer(welcome_text)
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        await message.answer("ይቅርታ፣ በስርዓቱ ላይ ችግር አጋጥሟል፣ በኋላ ይሞክሩ።")

# 4. /balance handler (ሙከራ)
@dp.message(Command("balance"))
async def balance_handler(message: types.Message):
    user_id = message.from_user.id
    try:
        response = supabase.table("users").select("balance").eq("user_id", user_id).execute()
        if response.data:
            balance = response.data[0]['balance']
            await message.answer(f"የእርስዎ የአሁኑ ሂሳብ፡ {balance} ብር ነው 💰")
        else:
            await message.answer("እባክዎ መጀመሪያ /start ብለው ይመዝገቡ።")
    except Exception as e:
        await message.answer("የሂሳብ መረጃን በማምጣት ላይ ችግር ተፈጥሯል።")

# 5. Run the bot
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
