import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL)


def init_db():
    conn = get_db()

    with conn.cursor() as cur:

        # ================= USERS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # ================= BALANCES =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS balances(
            user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,

            deposit_balance DOUBLE PRECISION DEFAULT 0,

            earned_balance DOUBLE PRECISION DEFAULT 0,

            advertising_balance DOUBLE PRECISION DEFAULT 0
        );
        """)

        # ================= CHANNELS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS channels(

            id SERIAL PRIMARY KEY,

            channel_id BIGINT UNIQUE,

            channel_username TEXT,

            channel_name TEXT,

            reward DOUBLE PRECISION DEFAULT 0.5,

            target_count INTEGER,

            current_count INTEGER DEFAULT 0,

            is_active BOOLEAN DEFAULT TRUE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """)

        # ================= BOTS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS bots(

            id SERIAL PRIMARY KEY,

            bot_username TEXT UNIQUE,

            bot_name TEXT,

            reward DOUBLE PRECISION DEFAULT 0.5,

            target_count INTEGER,

            current_count INTEGER DEFAULT 0,

            is_active BOOLEAN DEFAULT TRUE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """)

        # ================= ADS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS ads(

            id SERIAL PRIMARY KEY,

            user_id BIGINT REFERENCES users(user_id),

            username TEXT,

            ad_type TEXT,

            target_count INTEGER,

            current_count INTEGER DEFAULT 0,

            reward DOUBLE PRECISION DEFAULT 0.5,

            total_price DOUBLE PRECISION,

            status TEXT DEFAULT 'pending',

            is_active BOOLEAN DEFAULT FALSE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """)

        # ================= COMPLETED TASKS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS completed_tasks(

            id SERIAL PRIMARY KEY,

            user_id BIGINT,

            task_type TEXT,

            task_id INTEGER,

            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id,task_type,task_id)

        );
        """)

        # ================= REFERRALS =================

        cur.execute("""
        CREATE TABLE IF NOT EXISTS referrals(

            id SERIAL PRIMARY KEY,

            referrer_id BIGINT,

            referred_id BIGINT UNIQUE,

            reward_given BOOLEAN DEFAULT FALSE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        );
        """)

    conn.commit()

    conn.close()

    print("✅ Database Initialized")


# ============================================
# USER FUNCTIONS
# ============================================

def add_user(user_id, username, first_name):

    conn = get_db()

    with conn.cursor() as cur:

        cur.execute("""

        INSERT INTO users(user_id,username,first_name)

        VALUES(%s,%s,%s)

        ON CONFLICT(user_id)

        DO NOTHING

        """,(user_id,username,first_name))

        cur.execute("""

        INSERT INTO balances(user_id)

        VALUES(%s)

        ON CONFLICT(user_id)

        DO NOTHING

        """,(user_id,))

    conn.commit()

    conn.close()


def get_balance(user_id):

    conn=get_db()

    with conn.cursor() as cur:

        cur.execute("""

        SELECT

        deposit_balance,

        earned_balance,

        advertising_balance

        FROM balances

        WHERE user_id=%s

        """,(user_id,))

        data=cur.fetchone()

    conn.close()

    return data