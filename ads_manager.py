import psycopg
from db import get_db

class AdsManager:
    """Central brain for managing advertisements/campaigns"""
    
    @staticmethod
    def get_active_ads(ad_type: str = None):
        conn = get_db()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT id, link, target_count, current_count, price, type 
                    FROM ads 
                    WHERE is_active = TRUE AND status = 'active'
                """
                if ad_type:
                    query += " AND type = %s"
                    cur.execute(query, (ad_type,))
                else:
                    cur.execute(query)
                return cur.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_ad_progress(ad_id: int, user_id: int):
        conn = get_db()
        try:
            with conn.cursor() as cur:
                # 1. Check if user already completed this ad
                cur.execute("SELECT 1 FROM completed_ads WHERE user_id = %s AND ad_id = %s", (user_id, ad_id))
                if cur.fetchone():
                    return {"success": False, "message": "✅ You already completed this task!"}

                # 2. Update ad progress
                cur.execute("""
                    UPDATE ads 
                    SET current_count = current_count + 1 
                    WHERE id = %s AND is_active = TRUE
                    RETURNING current_count, target_count, price
                """, (ad_id,))
                
                result = cur.fetchone()
                if not result:
                    return {"success": False, "message": "❌ This campaign is no longer active."}

                current, target, price = result

                # 3. Mark as completed for this user
                cur.execute("INSERT INTO completed_ads (user_id, ad_id) VALUES (%s, %s)", (user_id, ad_id))

                # 4. Award user using 'amount' column (as per your DB structure)
                cur.execute("""
                    INSERT INTO balances (user_id, amount) 
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET amount = balances.amount + EXCLUDED.amount
                """, (user_id, price))

                # 5. Check if campaign is finished
                if current + 1 >= target:
                    cur.execute("UPDATE ads SET is_active = FALSE, status = 'completed' WHERE id = %s", (ad_id,))

                conn.commit()
                return {
                    "