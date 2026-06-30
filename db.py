import psycopg
import os
from config import DATABASE_URL

def get_db():
    return psycopg.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        balance NUMERIC DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id SERIAL PRIMARY KEY,
        bot_username TEXT UNIQUE,
        bot_name TEXT,
        is_active BOOLEAN DEFAULT TRUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_bot_tasks (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        bot_id INT,
        UNIQUE(user_id, bot_id)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()