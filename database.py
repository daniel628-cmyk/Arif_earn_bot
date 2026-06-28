import psycopg2
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def connect_db():
    pass # ነባር ኮድህ

def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        # ነባር ሰንጠረዦችህ (እነዚህን አትቀይር)
        cur.execute("CREATE TABLE IF NOT EXISTS users(user_id BIGINT PRIMARY KEY, username TEXT, balance NUMERIC DEFAULT 0);")
        cur.execute("CREATE TABLE IF NOT EXISTS channels(id SERIAL PRIMARY KEY, channel_id BIGINT UNIQUE, channel_link TEXT, channel_name TEXT, required_subs INT DEFAULT 1, is_active BOOLEAN DEFAULT TRUE);")
        
        # አዲሶቹ ሰንጠረዦች ለ Join Bot
        cur.execute("CREATE TABLE IF NOT EXISTS bots(id SERIAL PRIMARY KEY, bot_username TEXT UNIQUE, bot_name TEXT, is_active BOOLEAN DEFAULT TRUE);")
        cur.execute("CREATE TABLE IF NOT EXISTS user_bot_tasks(id SERIAL PRIMARY KEY, user_id BIGINT, bot_id INT, UNIQUE(user_id, bot_id));")
    conn.commit()
    conn.close()

def mark_bot_as_done(user_id, bot_id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM user_bot_tasks WHERE user_id = %s AND bot_id = %s", (user_id, bot_id))
        if cur.fetchone():
            conn.close()
            return False
        cur.execute("INSERT INTO user_bot_tasks (user_id, bot_id) VALUES (%s, %s)", (user_id, bot_id))
        cur.execute("UPDATE users SET balance = balance + 50 WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
    return True