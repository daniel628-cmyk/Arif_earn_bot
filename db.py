import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        # የነበሩት ሰንጠረዦች
        cur.execute("""
            CREATE TABLE IF NOT EXISTS channels(
                id SERIAL PRIMARY KEY, 
                channel_id BIGINT UNIQUE, 
                channel_link TEXT, 
                channel_name TEXT, 
                is_active BOOLEAN DEFAULT TRUE, 
                limit_count INT DEFAULT 0, 
                current_count INT DEFAULT 0
            );
        """)
        
        # አዲሱ ሰንጠረዥ - ለባላንስ
        cur.execute("""
            CREATE TABLE IF NOT EXISTS balances(
                user_id BIGINT PRIMARY KEY, 
                amount FLOAT DEFAULT 0
            );
        """)
        
        # አዲሱ ሰንጠረዥ - ለማስታወቂያ (ads)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads(
                id SERIAL PRIMARY KEY, 
                user_id BIGINT, 
                link TEXT, 
                price FLOAT, 
                status TEXT DEFAULT 'pending'
            );
        """)
    conn.commit()
    conn.close()

def update_and_check_limit(table_name, task_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {table_name} SET current_count = current_count + 1 WHERE id = %s", (task_id,))
        cur.execute(f"SELECT current_count, limit_count FROM {table_name} WHERE id = %s", (task_id,))
        res = cur.fetchone()
        if res and res[0] >= res[1]:
            cur.execute(f"UPDATE {table_name} SET is_active = FALSE WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()