from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from db import get_db
from config import ADMIN_ID

router = Router()

@router.message(Command("addbalance"))
async def add_balance(message: Message):
    # አድሚን መሆኑን ያረጋግጣል
    if message.from_user.id != ADMIN_ID:
        return 

    # ትዕዛዙን ይለያል: /addbalance [user_id] [amount]
    args = message.text.split()
    if len(args) < 3:
        return await message.answer("⚠️ አጠቃቀም: /addbalance [user_id] [amount]")

    target_user_id = args[1]
    amount = float(args[2])

    conn = get_db()
    cur = conn.cursor()
    
    # ባላንስ መኖሩን ይፈትሻል
    cur.execute("SELECT amount FROM balances WHERE user_id = %s", (target_user_id,))
    row = cur.fetchone()

    if row:
        cur.execute("UPDATE balances SET amount = amount + %s WHERE user_id = %s", (amount, target_user_id))
    else:
        cur.execute("INSERT INTO balances (user_id, amount) VALUES (%s, %s)", (target_user_id, amount))
    
    conn.commit()
    conn.close()
    
    await message.answer(f"✅ ለተጠቃሚ {target_user_id} የ {amount} ብር ባላንስ ተጨምሯል።")
    
    # ለተጠቃሚው ማሳወቂያ ይልካል
    try:
        await message.bot.send_message(target_user_id, f"⚡️ Congratulations! {amount} Birr has been added to your balance.")
    except Exception as e:
        print(f"Error sending notification to user: {e}")