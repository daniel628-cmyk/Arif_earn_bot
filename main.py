import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from supabase import create_client

# 1. Variables ከ Railway environment እንዲያነብ ይደረጋል
API_TOKEN = os.getenv('API_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# ቶከን ካልተገኘ ቦቱ እንዳይcrash
if not API_TOKEN:
    raise ValueError("API_TOKEN አልተገኘም! በ Railway Variables ውስጥ ያስገቡት።")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- ዋናው ሜኑ ---
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots"))
    builder.row(KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw"))
    builder.row(KeyboardButton(text="📢 Advertise"))
    return builder.as_markup(resize_keyboard=True)

# --- Start Command ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    check_user = supabase.table("users").select("user_id").eq("user_id", user_id).execute()
    
    if len(check_user.data) == 0:
        supabase.table("users").insert({"user_id": user_id, "balance": 0.0}).execute()
        
    await message.answer(
        f"ሰላም {message.from_user.first_name}!\n\n"
        "ወደ Arif Earning Bot እንኳን በደህና መጡ! ቻናሎችን እና ቦቶችን በመቀላቀል ገንዘብ ማግኘት ይጀምሩ።",
        reply_markup=get_main_menu()
    )

# --- ቻናል ዝርዝር ---
@dp.message(F.text == "📢 Join Channels")
async def show_tasks(message: types.Message):
    tasks = supabase.table("tasks").select("*").eq("task_type", "channel").execute().data
    if not tasks:
        await message.answer("❌ በአሁኑ ሰዓት የሚገኙ ስራዎች የሉም።")
        return

    builder = InlineKeyboardBuilder()
    for task in tasks:
        builder.row(InlineKeyboardButton(text=f"✅ {task['task_name']} (0.25 ብር)", callback_data=f"join_{task['task_id']}"))
    await message.answer("📢 የሚከተሉትን ቻናሎች ይቀላቀሉ፦", reply_markup=builder.as_markup())

# --- የቻናል ማረጋገጫ ---
@dp.callback_query(F.data.startswith("join_"))
async def join_task(callback: types.CallbackQuery):
    task_id = callback.data.split("_")[1]
    task = supabase.table("tasks").select("*").eq("task_id", task_id).execute().data[0]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 ሊንኩን ይክፈቱ", url=task['target_link'])],
        [InlineKeyboardButton(text="✅ አድርጌያለሁ", callback_data=f"check_{task_id}")]
    ])
    await callback.message.answer(f"ተልዕኮ: {task['task_name']}\nቻናሉን ይቀላቀሉና 'አድርጌያለሁ' ይጫኑ።", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(F.data.startswith("check_"))
async def verify_task(callback: types.CallbackQuery):
    task_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    task = supabase.table("tasks").select("*").eq("task_id", task_id).execute().data[0]
    
    try:
        chat_member = await bot.get_chat_member(chat_id=task['target_link'], user_id=user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            # ተጠቃሚው ቀድሞ ሰርቶት እንደሆነ ፈትሽ
            exists = supabase.table("user_tasks").select("id").eq("user_id", user_id).eq("task_id", task_id).execute()
            if len(exists.data) > 0:
                await callback.answer("❌ ቀድመው ሰርተውታል!", show_alert=True)
                return

            # ባላንስ አዘምን እና መዝግብ
            user = supabase.table("users").select("balance").eq("user_id", user_id).execute().data[0]
            new_balance = user['balance'] + 0.25
            supabase.table("users").update({"balance": new_balance}).eq("user_id", user_id).execute()
            supabase.table("user_tasks").insert({"user_id": user_id, "task_id": task_id, "status": "active"}).execute()
            await callback.message.answer("✅ ስኬታማ! 0.25 ብር ተሞልቶልዎታል።")
        else:
            await callback.message.answer("❌ ቻናሉን አልተቀላቀሉም።")
    except Exception:
        await callback.message.answer("⚠️ ስህተት ተፈጥሯል፣ የቦቱን አድሚንነት ያረጋግጡ።")
    await callback.answer()

if __name__ == '__main__':
    dp.run_polling(bot)
