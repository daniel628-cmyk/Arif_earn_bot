from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from db import get_db
from config import ADMIN_ID

router = Router()

@router.message(F.text == "📢 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ (ለምሳሌ: https://t.me/username) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)

# ... (እዚህ ጋር የሊንክ እና የሰዎች ብዛት መጠየቂያዎችህ ይገባሉ) ...

@router.message(AdvertiseState.waiting_for_price)
async def finalize_ad(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = message.from_user.id
    link = data['link']
    members = data['members']
    total_price = members * 0.5  # 1 ሰው = 0.5 ብር

    conn = get_db()
    with conn.cursor() as cur:
        # ባላንስ ያረጋግጡ
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        balance = cur.fetchone()
        current_balance = balance[0] if balance else 0

        if current_balance >= total_price:
            # ባላንስ ካለ አጽድቀው
            cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (total_price, user_id))
            cur.execute("INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, 'active')", 
                        (user_id, link, members, total_price))
            await message.answer("✅ ባላንስ ስላለህ ማስታወቂያህ በራስ-ሰር ተጀምሯል!")
        else:
            # ባላንስ ከሌለ ለአድሚን ላክ
            cur.execute("INSERT INTO ads (user_id, link, target_count, price, status) VALUES (%s, %s, %s, %s, 'pending')", 
                        (user_id, link, members, total_price))
            await message.answer("⚠️ ባላንስህ በቂ ስላልሆነ ማስታወቂያህ ለአድሚን ተልኳል።")
            await bot.send_message(ADMIN_ID, f"📢 አዲስ Pending ማስታወቂያ! ID: {user_id}")
        
        conn.commit()
    conn.close()
    await state.clear()