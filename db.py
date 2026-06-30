import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    # Psycopg 3 አጠቃቀም
    return psycopg.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        # የቻናል ሰንጠረዥ (limit እና current_count ተጨምሯል)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS channels(
                id SERIAL PRIMARY KEY, 
                channel_id BIGINT UNIQUE, 
                channel_link TEXT, 
                channel_name TEXT, 
                required_subs INT DEFAULT 1, 
                is_active BOOLEAN DEFAULT TRUE,
                limit_count INT DEFAULT 0,
                current_count INT DEFAULT 0
            );
        """)
        # የቦት ሰንጠረዥ (limit እና current_count ተጨምሯል)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bots(
                id SERIAL PRIMARY KEY, 
                bot_username TEXT UNIQUE, 
                bot_name TEXT, 
                is_active BOOLEAN DEFAULT TRUE,
                limit_count INT DEFAULT 0,
                current_count INT DEFAULT 0
            );
        """)
    conn.commit()
    conn.close()

def update_task_count(table_name, task_id):
    """
    ተጠቃሚ ሲያረጋግጥ (Verify) ብዛቱን ይቆጥራል፣ 
    ገደቡ ሲሞላ ራሱ በራሱ is_activeን FALSE ያደርገዋል።
    """
    conn = get_db()
    with conn.cursor() as cur:
        # ብዛቱን በ 1 ጨምር
        cur.execute(f"UPDATE {table_name} SET current_count = current_count + 1 WHERE id = %s", (task_id,))
        
        # ገደቡ ላይ መድረሱን አረጋግጥ
        cur.execute(f"SELECT current_count, limit_count FROM {table_name} WHERE id = %s", (task_id,))
        res = cur.fetchone()
        
        if res:
            current, limit = res
            # ብዛቱ ከገደቡ ሲበልጥ ወይም እኩል ሲሆን ከማስታወቂያው ዝርዝር ውስጥ አጥፋው
            if current >= limit and limit > 0:
                cur.execute(f"UPDATE {table_name} SET is_active = FALSE WHERE id = %s", (task_id,))
    
    conn.commit()
    conn.close()

def get_db_connection():
    return get_db()