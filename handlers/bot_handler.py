from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_db, mark_bot_as_done

router = Router()

@router.message(F.text == "🤖 Join Bots")
async def join_bots_handler(message: Message):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # ከዳታቤዝ ውስጥ ንቁ የሆኑ ቦቶችን መምረጥ
            cur.execute("SELECT id, bot_username, bot_name FROM bots WHERE is_active = TRUE")
            bots = cur.fetchall()
            
        if not bots:
            await message.answer("በአሁኑ ሰዓት ምንም ቦት የለም።")
            return

        # ለእያንዳንዱ ቦት የInline Button መፍጠር
        for b_id, username, name in bots:
            # ለተጠቃሚው በቀጥታ ወደ ቦቱ የሚወስድ ሊንክ እና የማረጋገጫ በተን
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="ወደ ቦቱ ሂድ", url=f"https://t.me/{username}")],
                [InlineKeyboardButton(text="✅ አረጋግጥ (Verify)", callback_data=f"vb_{b_id}")]
            ])
            
            await message.answer(f"ቦት፡ **{name}**\n\nከላይ ያለውን ሊንክ በመጠቀም ቦቱን ይቀላቀሉ። ከዛም 'አረጋግጥ' የሚለውን ይጫኑ።", 
                                 reply_markup=keyboard, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error fetching bots: {e}")
        await message.answer("ይቅርታ፣ በቴክኒክ ችግር ቦቶችን ማምጣት አልቻልኩም።")

@router.callback_query(F.data.startswith("vb_"))
async def verify_bot_callback(callback: CallbackQuery):
    # ከ callback_data ውስጥ የቦቱን ID መውሰድ
    bot_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # ነጥብ የመጨመር እና የመመዝገብ ስራ
    if mark_bot_as_done(user_id, bot_id):
        await callback.answer("✅ ተሳክቷል! 50 ብር ተጨምሮልዎታል!", show_alert=True)
    else:
        await callback.answer("⚠️ ይህን ቦት ቀድመው ሰርተውታል ወይም ነጥብ አግኝተውበታል!", show_alert=True)