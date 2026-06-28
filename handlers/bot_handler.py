import psycopg2
import os

# ከ Railway/Supabase የምታገኘው የዳታቤዝ ግንኙነት
DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

def get_db():
    return conn

def init_db():
    """ሁሉንም ሰንጠረዦች በኮድ መፍጠር"""
    with conn.cursor() as cur:
        # 1. የተጠቃሚዎች ሰንጠረዥ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance NUMERIC DEFAULT 0
        );
        """)
        
        # 2. የቻናሎች ሰንጠረዥ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            id SERIAL PRIMARY KEY,
            channel_id BIGINT UNIQUE NOT NULL,
            channel_link TEXT NOT NULL,
            channel_name TEXT NOT NULL,
            required_subs INT DEFAULT 1,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)
        
        # 3. የቦቶች ሰንጠረዥ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bots(
            id SERIAL PRIMARY KEY,
            bot_username TEXT UNIQUE NOT NULL,
            bot_name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)
        
        # 4. የቦት ስራዎች መከታተያ ሰንጠረዥ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_bot_tasks(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            bot_id INT,
            UNIQUE(user_id, bot_id)
        );
        """)
        
    conn.commit()
    print("✅ All Tables (Users, Channels, Bots, Bot Tasks) initialized successfully!")

def mark_bot_as_done(user_id, bot_id):
    """ተጠቃሚው ቦቱን እንደሰራ መመዝገብ እና ነጥብ መጨመር"""
    with conn.cursor() as cur:
        # አስቀድሞ ሰርቶት እንደሆነ ፈትሽ
        cur.execute("SELECT 1 FROM user_bot_tasks WHERE user_id = %s AND bot_id = %s", (user_id, bot_id))
        if cur.fetchone():
            return False 
        
        # መዝግበው እና ብር ጨምርለት
        cur.execute("INSERT INTO user_bot_tasks (user_id, bot_id) VALUES (%s, %s)", (user_id, bot_id))
        cur.execute("UPDATE users SET balance = balance + 50 WHERE user_id = %s", (user_id,))
        conn.commit()
        return True