import psycopg
from config import DATABASE_URL


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        balance NUMERIC DEFAULT 0,
        referred_by BIGINT DEFAULT NULL
    );
    """)

    # Channels
    cur.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id SERIAL PRIMARY KEY,
        channel_username TEXT UNIQUE,
        channel_name TEXT,
        is_active BOOLEAN DEFAULT TRUE
    );
    """)

    # Bots
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id SERIAL PRIMARY KEY,
        bot_username TEXT UNIQUE,
        bot_name TEXT,
        is_active BOOLEAN DEFAULT TRUE
    );
    """)

    # Completed Bot Tasks
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_bot_tasks (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        bot_id INT,
        UNIQUE(user_id, bot_id)
    );
    """)

    # Completed Channel Tasks
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_channel_tasks (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        channel_id INT,
        UNIQUE(user_id, channel_id)
    );
    """)

    conn.commit()
    cur.close()
    conn.close()


# ---------------- USERS ----------------

def add_user(user_id, username):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users(user_id, username)
        VALUES(%s,%s)
        ON CONFLICT(user_id) DO NOTHING
    """, (user_id, username))

    conn.commit()
    cur.close()
    conn.close()


def get_balance(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT balance FROM users WHERE user_id=%s",
        (user_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return row[0]

    return 0


# ---------------- BOTS ----------------

def get_bots():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, bot_username, bot_name
        FROM bots
        WHERE is_active=TRUE
    """)

    bots = cur.fetchall()

    cur.close()
    conn.close()

    return bots


def mark_bot_done(user_id, bot_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM user_bot_tasks WHERE user_id=%s AND bot_id=%s",
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


# ---------------- CHANNELS ----------------

def get_channels():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, channel_username, channel_name
        FROM channels
        WHERE is_active=TRUE
    """)

    channels = cur.fetchall()

    cur.close()
    conn.close()

    return channels


def mark_channel_done(user_id, channel_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM user_channel_tasks WHERE user_id=%s AND channel_id=%s",
        (user_id, channel_id)
    )

    if cur.fetchone():
        cur.close()
        conn.close()
        return False

    cur.execute(
        "INSERT INTO user_channel_tasks(user_id, channel_id) VALUES(%s,%s)",
        (user_id, channel_id)
    )

    cur.execute(
        "UPDATE users SET balance=balance+50 WHERE user_id=%s",
        (user_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return True