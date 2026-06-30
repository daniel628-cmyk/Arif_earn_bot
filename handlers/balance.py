from aiogram import Router, F
from aiogram.types import Message
from db import get_db

router = Router()

@router.message(F.text == "💰 Balance")
async def check_balance(message: Message):
    user_id = message.from_user.id
    
    # get_db() የሚያመጣው connection/pool ነው ብለን እንገምታለን
    conn = get_db()
    
    try:
        with conn.cursor() as cur:
            # psycopg 3 syntax
            cur.execute("SELECT amount FROM balances WHERE user_id = %s", (user_id,))
            res = cur.fetchone()
            
            if res:
                amount = res[0]
            else:
                cur.execute("INSERT INTO balances (user_id, amount) VALUES (%s, 0)", (user_id,))
                conn.commit()
                amount = 0
                
        await message.answer(f"💰 የአሁኑ ባላንስዎ፡ {amount} ብር ነው")
        
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
    finally:
        conn.close()