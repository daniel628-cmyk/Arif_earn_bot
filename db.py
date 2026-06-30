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
def get_bots():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, bot_username, bot_name
        FROM bots
        WHERE is_active = TRUE
    """)

    bots = cur.fetchall()

    cur.close()
    conn.close()

    return bots


def mark_bot_done(user_id, bot_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM user_bot_tasks WHERE user_id=%s AND bot_id=%s",
        (user_id, bot_id)
    )

    if cur.fetchone():
        cur.close()
        conn.close()
        return False

    cur.execute(
        "INSERT INTO user_bot_tasks(user_id, bot_id) VALUES(%s,%s)",
        (user_id, bot_id)
    )

    cur.execute(
        "UPDATE users SET balance=balance+50 WHERE user_id=%s",
        (user_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return True