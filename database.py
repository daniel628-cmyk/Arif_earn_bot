import os
import psycopg
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

# ለግንኙነት (Connection)
conn = None

def connect_db():
    global conn
    try:
        conn = psycopg.connect(DATABASE_URL)
        print("✅ Database Connected")
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def get_db():
    return conn

def init_db():
    """ሰንጠረዦችን መፈተሽ እና መፍጠር"""
    with conn.cursor() as cur:
        # የተጠቃሚዎች ሰንጠረዥ
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance NUMERIC DEFAULT 0
        );
        """)
        
        # የቻናሎች ሰንጠረዥ (አዲስ)
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
        
    conn.commit()
    print("✅ Tables checked/initialized successfully!")

# አስፈላጊ ከሆነ ሲዘጋ ይጠቀሙበት
def close_db():
    if conn:
        conn.close()