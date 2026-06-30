import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL)


def connect_db():
    conn = get_db()
    print("✅ Database Connected")
    conn.close()


def init_db():
    conn = get_db()

    with conn.cursor() as cur:

        # Users
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance NUMERIC DEFAULT 0,
            referred_by BIGINT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Channels
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            id SERIAL PRIMARY KEY,
            channel_username TEXT UNIQUE,
            channel_name TEXT,
            reward INTEGER DEFAULT 10,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)

        # Bots
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bots(
            id SERIAL PRIMARY KEY,
            bot_username TEXT UNIQUE,
            bot_name TEXT,
            reward INTEGER DEFAULT 50,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)

        # Joined Channels
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_channel_tasks(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            channel_id INTEGER,
            UNIQUE(user_id, channel_id)
        );
        """)

        # Joined Bots
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_bot_tasks(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            bot_id INTEGER,
            UNIQUE(user_id, bot_id)
        );
        """)

        # Withdraw Requests
        cur.execute("""
        CREATE TABLE IF NOT EXISTS withdraws(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            amount NUMERIC,
            wallet TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Advertisements
        cur.execute("""
        CREATE TABLE IF NOT EXISTS advertisements(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            ad_type TEXT,
            target TEXT,
            amount NUMERIC,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    conn.commit()
    conn.close()


# ==========================
# USER FUNCTIONS
# ==========================

def add_user(user_id, username):
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO users(user_id, username)
        VALUES(%s,%s)
        ON CONFLICT(user_id)
        DO NOTHING
        """, (user_id, username))

    conn.commit()
    conn.close()


def get_balance(user_id):
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT balance FROM users WHERE user_id=%s",
            (user_id,)
        )

        row = cur.fetchone()

    conn.close()

    if row:
        return row[0]

    return 0


def add_balance(user_id, amount):
    conn = get_db()

    with conn.cursor() as cur:
        cur.execute("""
        UPDATE users
        SET balance = balance + %s
        WHERE user_id=%s
        """, (amount, user_id))

    conn.commit()
    conn.close()