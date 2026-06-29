import os
import psycopg

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL)


def connect_db():
    print("✅ Database Connected")


def init_db():
    conn = get_db()

    with conn.cursor() as cur:

        # Users
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            balance NUMERIC DEFAULT 0
        );
        """)

        # Channels
        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(
            id SERIAL PRIMARY KEY,
            channel_username TEXT UNIQUE,
            channel_name TEXT,
            reward NUMERIC DEFAULT 50,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)

        # Bots
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bots(
            id SERIAL PRIMARY KEY,
            bot_username TEXT UNIQUE,
            bot_name TEXT,
            reward NUMERIC DEFAULT 50,
            is_active BOOLEAN DEFAULT TRUE
        );
        """)

        # Joined Channels
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_channel_tasks(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            channel_id INT,
            UNIQUE(user_id, channel_id)
        );
        """)

        # Joined Bots
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_bot_tasks(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            bot_id INT,
            UNIQUE(user_id, bot_id)
        );
        """)

    conn.commit()
    conn.close()


# ================= BOT =================

def mark_bot_as_done(user_id, bot_id):
    conn = get_db()

    with conn.cursor() as cur:

        cur.execute(
            "SELECT * FROM user_bot_tasks WHERE user_id=%s AND bot_id=%s",
            (user_id, bot_id)
        )

        if cur.fetchone():
            conn.close()
            return False

        cur.execute(
            "INSERT INTO user_bot_tasks(user_id, bot_id) VALUES(%s,%s)",
            (user_id, bot_id)
        )

        cur.execute("""
        UPDATE users
        SET balance = balance + (
            SELECT reward FROM bots WHERE id=%s
        )
        WHERE user_id=%s
        """, (bot_id, user_id))

    conn.commit()
    conn.close()

    return True


# ================= CHANNEL =================

def mark_channel_as_done(user_id, channel_id):
    conn = get_db()

    with conn.cursor() as cur:

        cur.execute(
            "SELECT * FROM user_channel_tasks WHERE user_id=%s AND channel_id=%s",
            (user_id, channel_id)
        )

        if cur.fetchone():
            conn.close()
            return False

        cur.execute(
            "INSERT INTO user_channel_tasks(user_id, channel_id) VALUES(%s,%s)",
            (user_id, channel_id)
        )

        cur.execute("""
        UPDATE users
        SET balance = balance + (
            SELECT reward FROM channels WHERE id=%s
        )
        WHERE user_id=%s
        """, (channel_id, user_id))

    conn.commit()
    conn.close()

    return True


# ================= USERS =================

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


# ================= ADMIN =================

def add_bot(bot_username, bot_name, reward):
    conn = get_db()

    with conn.cursor() as cur:

        cur.execute("""
        INSERT INTO bots(bot_username, bot_name, reward)
        VALUES(%s,%s,%s)
        """, (bot_username, bot_name, reward))

    conn.commit()
    conn.close()


def add_channel(channel_username, channel_name, reward):
    conn = get_db()

    with conn.cursor() as cur:

        cur.execute("""
        INSERT INTO channels(channel_username, channel_name, reward)
        VALUES(%s,%s,%s)
        """, (channel_username, channel_name, reward))

    conn.commit()
    conn.close()