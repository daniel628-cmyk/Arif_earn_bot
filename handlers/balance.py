from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COALESCE(deposit_balance, 0) as deposit,
                    COALESCE(earned_balance, 0) as earned
                FROM balances 
                WHERE user_id = %s
            """, (user_id,))
            
            row = cur.fetchone()
            
            if not row:
                # Create record if user doesn't exist
                cur.execute("""
                    INSERT INTO balances (user_id, deposit_balance, earned_balance)
                    VALUES (%s, 0, 0)
                """, (user_id,))
                deposit = 0.0
                earned = 0.0
            else:
                deposit = row[0]
                earned = row[1]

        total = deposit + earned

        await message.answer(
            f"💰 **Your Balance**\n\n"
            f"📥 Deposited: **{deposit:.2f}** Birr\n"
            f"💵 Earned: **{earned:.2f}** Birr\n\n"
            f"🔢 **Total: {total:.2f}** Birr"
        )
        
    except Exception as e:
        await message.answer("❌ Error fetching balance. Please try again.")
        print(f"Balance error: {e}")
    finally:
        conn.close()