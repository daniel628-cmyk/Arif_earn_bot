import psycopg
import os
from datetime import datetime

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
                earned_balance DOUBLE PRECISION DEFAULT 0
            );
        """)

        # ================= ADS (Campaigns) =================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ads(
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                link TEXT NOT NULL,
                type TEXT CHECK (type IN ('channel', 'bot')),
                target_count INTEGER NOT NULL,
                current_count INTEGER DEFAULT 0,
                reward DOUBLE PRECISION DEFAULT 0.5,
                total_price DOUBLE PRECISION,
                status TEXT DEFAULT 'active',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # ================= COMPLETED TASKS =================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS completed_ads(
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                ad_id INTEGER REFERENCES ads(id),
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, ad_id)
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

        # ================= WITHDRAWALS =================
        cur.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals(
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                amount DOUBLE PRECISION,
                phone TEXT,
                full_name TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    conn.commit()
    conn.close()
    print("✅ Database tables initialized successfully!")

# Helper Functions
def add_user(user_id, username, first_name):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, username, first_name))
        
        cur.execute("""
            INSERT INTO balances (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))
    conn.commit()
    conn.close()