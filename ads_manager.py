from db import get_db

REWARD_PER_USER = 0.5

class AdsManager:

    @staticmethod
    def get_active_ads(ad_type=None):
        """Get active ads for users to join"""
        conn = get_db()
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT id, user_id, link, target_count, current_count, type
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
    def create_ad(user_id: int, link: str, target_count: int, ad_type: str):
        """Create new ad campaign"""
        total_price = target_count * REWARD_PER_USER

        conn = get_db()
        try:
            with conn.cursor() as cur:
                # Check deposit balance
                cur.execute("SELECT deposit_balance FROM balances WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                if not row or row[0] < total_price:
                    return {"success": False, "message": "❌ Not enough deposit balance."}

                # Deduct deposit
                cur.execute("""
                    UPDATE balances SET deposit_balance = deposit_balance - %s WHERE user_id = %s
                """, (total_price, user_id))

                # Create ad
                cur.execute("""
                    INSERT INTO ads (user_id, link, target_count, price, type, status, is_active)
                    VALUES (%s, %s, %s, %s, %s, 'active', TRUE)
                    RETURNING id
                """, (user_id, link, target_count, REWARD_PER_USER, ad_type))

                ad_id = cur.fetchone()[0]
                conn.commit()

                return {"success": True, "ad_id": ad_id, "price": total_price}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": str(e)}
        finally:
            conn.close()

    @staticmethod
    def update_ad_progress(ad_id: int, user_id: int):
        """Verify task and reward user"""
        conn = get_db()
        try:
            with conn.cursor() as cur:
                # Get ad
                cur.execute("""
                    SELECT user_id as owner_id, current_count, target_count 
                    FROM ads WHERE id = %s AND is_active = TRUE
                """, (ad_id,))
                ad = cur.fetchone()
                if not ad:
                    return {"success": False, "message": "❌ Campaign is closed."}

                owner_id, current, target = ad
                if owner_id == user_id:
                    return {"success": False, "message": "❌ You cannot complete your own ad."}

                # Check if already completed
                cur.execute("SELECT 1 FROM completed_ads WHERE user_id = %s AND ad_id = %s", (user_id, ad_id))
                if cur.fetchone():
                    return {"success": False, "message": "✅ You already completed this task."}

                # Mark completed
                cur.execute("INSERT INTO completed_ads (user_id, ad_id) VALUES (%s, %s)", (user_id, ad_id))

                # Give reward
                cur.execute("UPDATE balances SET earned_balance = earned_balance + %s WHERE user_id = %s", 
                           (REWARD_PER_USER, user_id))

                # Update progress
                cur.execute("UPDATE ads SET current_count = current_count + 1 WHERE id = %s RETURNING current_count", (ad_id,))
                new_current = cur.fetchone()[0]

                completed = new_current >= target
                if completed:
                    cur.execute("UPDATE ads SET is_active = FALSE, status = 'completed' WHERE id = %s", (ad_id,))

                conn.commit()

                return {
                    "success": True,
                    "completed": completed,
                    "message": f"🎉 +{REWARD_PER_USER} Birr added to your Earned Balance!"
                }
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": "❌ Error occurred."}
        finally:
            conn.close()