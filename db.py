import os
import random
import string
from datetime import datetime, timedelta

import psycopg


DATABASE_URL = os.getenv("DATABASE_URL")


def get_db():
    return psycopg.connect(DATABASE_URL)
def init_db():

    conn = get_db()

    try:

        with conn.cursor() as cur:

            # ================= USERS =================

            cur.execute("""

                CREATE TABLE IF NOT EXISTS users(

                    user_id BIGINT PRIMARY KEY,

                    username TEXT,

                    first_name TEXT,

                    is_banned BOOLEAN DEFAULT FALSE,

                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                );

            """)

            # ================= BALANCES =================

            cur.execute("""

                CREATE TABLE IF NOT EXISTS balances(

                    user_id BIGINT PRIMARY KEY
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    deposit_balance DOUBLE PRECISION DEFAULT 0,

                    earned_balance DOUBLE PRECISION DEFAULT 0

                );

            """)

            # ================= ADS =================

            cur.execute("""

                CREATE TABLE IF NOT EXISTS ads(

                    id SERIAL PRIMARY KEY,

                    user_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    link TEXT NOT NULL,

                    type TEXT CHECK(type IN ('channel','bot')),

                    target_count INTEGER NOT NULL,

                    current_count INTEGER DEFAULT 0,

                    reward DOUBLE PRECISION DEFAULT 0.27,

                    total_price DOUBLE PRECISION,

                    status TEXT DEFAULT 'active',

                    is_active BOOLEAN DEFAULT TRUE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    completed_at TIMESTAMP

                );

            """)

            # ================= COMPLETED ADS =================

            cur.execute("""

                CREATE TABLE IF NOT EXISTS completed_ads(

                    id SERIAL PRIMARY KEY,

                    user_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    ad_id INTEGER
                        REFERENCES ads(id)
                        ON DELETE CASCADE,

                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(user_id, ad_id)

                );

            """)

            # ================= VERIFICATION CODES =================

            cur.execute("""

                CREATE TABLE IF NOT EXISTS verification_codes(

                    id SERIAL PRIMARY KEY,

                    code TEXT UNIQUE,

                    ad_id INTEGER
                        REFERENCES ads(id)
                        ON DELETE CASCADE,

                    user_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    used BOOLEAN DEFAULT FALSE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    expires_at TIMESTAMP

                );

            """)

        conn.commit()

    finally:

        conn.close()