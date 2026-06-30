@router.message(AdvertiseState.waiting_for_amount)
async def get_amount(message: Message, state: FSMContext, bot: Bot):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ እባክዎን ቁጥር ብቻ ይላኩ።")
        return

    data = await state.get_data()
    link = data.get('link')
    user_id = message.from_user.id
    
    conn = get_db()
    with conn.cursor() as cur:
        # 1. የባላንስ ማረጋገጫ
        cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
        balance = cur.fetchone()
        
        user_balance = balance[0] if balance else 0

        if user_balance >= amount:
            # ባላንስ ካለው አውቶማቲካሊ አጽድቀው
            status = 'active'
            cur.execute("UPDATE balances SET amount = amount - %s WHERE user_id = %s", (amount, user_id))
            await message.answer("✅ ባላንስ ስላለህ ማስታወቂያህ በአውቶማቲክ ተጠናቋል!")
        else:
            # ባላንስ ከሌለው ለአድሚን ላክ
            status = 'pending'
            await message.answer("⚠️ ባላንስህ በቂ ስላልሆነ ማስታወቂያህ በአድሚን እስኪጸድቅ ይጠብቃል።")
        
        cur.execute(
            "INSERT INTO ads (user_id, link, price, status) VALUES (%s, %s, %s, %s) RETURNING id",
            (user_id, link, amount, status)
        )
        ad_id = cur.fetchone()[0]
        conn.commit()
    conn.close()

    # ለአድሚን ማሳወቂያ (pending ከሆነ ብቻ)
    if status == 'pending':
        await bot.send_message(ADMIN_ID, f"📢 አዲስ ማስታወቂያ! ID: {ad_id}\nባላንስ የለውም፣ ይገምግሙ።")

    await state.clear()