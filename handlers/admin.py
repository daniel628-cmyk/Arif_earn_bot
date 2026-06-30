from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from db import get_db

router = Router()  # ይህ መስመር የግድ መኖር አለበት!

# 1. አድሚን ባላንስ እንዲጨምርበት
@router.message(Command("add_balance"))
async def add_balance(message: Message):
    # አጠቃቀም፡ /add_balance [user_id] [amount]
    args = message.text.split()
    if len(args) < 3:
        await message.answer("⚠️ አጠቃቀም፡ /add_balance [user_id] [amount]")
        return
    
    try:
        user_id = int(args[1])
        amount = float(args[2])
    except ValueError:
        await message.answer("❌ እባክዎን ትክክለኛ user_id እና መጠን (ቁጥር) ያስገቡ።")
        return
    
    conn = get_db()
    with conn.cursor() as cur:
        # ባላንስ ካለ አዘምን፣ ከሌለ አዲስ አስገባ (UPSERT)
        cur.execute("""
            INSERT INTO balances (user_id, amount) 
            VALUES (%s, %s) 
            ON CONFLICT (user_id) 
            DO UPDATE SET amount = balances.amount + EXCLUDED.amount
        """, (user_id, amount))
        conn.commit()
    conn.close()
    
    await message.answer(f"✅ ለተጠቃሚ {user_id} {amount} ብር ተጨምሯል።")

# 2. የPending ማስታወቂያዎችን ማየት
@router.message(Command("admin_ads"))
async def show_pending_ads(message: Message):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT id, user_id, link, price FROM ads WHERE status = 'pending'")
        ads = cur.fetchall()
    conn.close()

    if not ads:
        await message.answer("✅ ምንም የተጠባባቂ (pending) ማስታወቂያ የለም።")
        return

    response = "📢 **የሚጠባበቁ ማስታወቂያዎች:**\n\n"
    for ad in ads:
        response += f"🆔 ID: {ad[0]} | 👤 User: {ad[1]}\n🔗 Link: {ad[2]}\n💰 Price: {ad[3]} ብር\n-------------------\n"
    
    response += "\nማስታወቂያ ለማጽደቅ፡ /approve [ID] ተጠቀም።"
    await message.answer(response)

# 3. ማስታወቂያ ማጽደቅ (status -> active)
@router.message(Command("approve"))
async def approve_ad(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ አጠቃቀም፡ /approve [ad_id]")
        return
    
    ad_id = args[1]
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE ads SET status = 'active' WHERE id = %s", (ad_id,))
        conn.commit()
    conn.close()
    
    await message.answer(f"✅ ማስታወቂያ ID: {ad_id} ተጸድቋል! አሁን ለተጠቃሚዎች ይታያል።")