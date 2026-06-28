from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db

router = Router()

@router.message(F.text == "🤖 Join Bots")
async def join_bots_handler(message: Message):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # ከዳታቤዝ ውስጥ ንቁ የሆኑ ቦቶችን መምረጥ
            cur.execute("SELECT bot_username, bot_name FROM bots WHERE is_active = TRUE")
            bots = cur.fetchall()
            
        if not bots:
            await message.answer("በአሁኑ ሰዓት ምንም ቦት የለም።")
            return

        # ለእያንዳንዱ ቦት የInline Button መፍጠር
        buttons = []
        for username, name in bots:
            # ለተጠቃሚው በቀጥታ ወደ ቦቱ የሚወስድ ሊንክ
            url = f"https://t.me/{username}"
            buttons.append([InlineKeyboardButton(text=name, url=url)])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.answer("ለማግኘት ከታች ያሉትን ቦቶች ይጠቀሙ፡", reply_markup=keyboard)
        
    except Exception as e:
        print(f"Error fetching bots: {e}")
        await message.answer("ይቅርታ፣ በቴክኒክ ችግር ቦቶችን ማምጣት አልቻልኩም።")