@staticmethod
    def update_ad_progress(ad_id: int, user_id: int):
        conn = get_db()
        try:
            with conn.cursor() as cur:
                # 1. ቼክ ማድረግ
                cur.execute("SELECT 1 FROM completed_ads WHERE user_id = %s AND ad_id = %s", (user_id, ad_id))
                if cur.fetchone():
                    return {"success": False, "message": "✅ ቀድመው ሰርተውታል!"}

                # 2. እድገት ማዘመን
                cur.execute("""
                    UPDATE ads SET current_count = current_count + 1 
                    WHERE id = %s AND is_active = TRUE
                    RETURNING current_count, target_count, price
                """, (ad_id,))
                
                result = cur.fetchone()
                if not result:
                    return {"success": False, "message": "❌ ይህ ማስታወቂያ ተዘግቷል።"}

                current, target, price = result
                
                # 3. ሽልማቱን ወደ 'amount' አምድ ማከል
                cur.execute("""
                    INSERT INTO balances (user_id, amount) 
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET amount = balances.amount + EXCLUDED.amount
                """, (user_id, price))

                cur.execute("INSERT INTO completed_ads (user_id, ad_id) VALUES (%s, %s)", (user_id, ad_id))

                if current + 1 >= target:
                    cur.execute("UPDATE ads SET is_active = FALSE, status = 'completed' WHERE id = %s", (ad_id,))

                conn.commit()
                return {"success": True, "message": f"✅ እንኳን ደስ አለዎት! {price} ብር ተጨምሮልዎታል።"}
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            return {"success": False, "message": "❌ ስህተት ተፈጥሯል።"}
        finally:
            conn.close()