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

                    type TEXT
                        CHECK(type IN ('channel','bot')),

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

                    completed_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP,

                    UNIQUE(user_id, ad_id)

                );
            """)

            # ================= REFERRALS =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS referrals(

                    id SERIAL PRIMARY KEY,

                    referrer_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    referred_id BIGINT UNIQUE
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    reward_given BOOLEAN DEFAULT FALSE,

                    reward_amount DOUBLE PRECISION DEFAULT 2,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                );
            """)

            # ================= WITHDRAWALS =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS withdrawals(

                    id SERIAL PRIMARY KEY,

                    user_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    amount DOUBLE PRECISION,

                    phone TEXT,

                    full_name TEXT,

                    status TEXT DEFAULT 'pending',

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    approved_at TIMESTAMP

                );
            """)
            # ================= VERIFICATION CODES =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS verification_codes(

                    id SERIAL PRIMARY KEY,

                    code TEXT UNIQUE NOT NULL,

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

            # ================= CHANNELS =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS channels(

                    id SERIAL PRIMARY KEY,

                    owner_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    username TEXT UNIQUE,

                    title TEXT,

                    is_active BOOLEAN DEFAULT TRUE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                );
            """)

            # ================= BOTS =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS bots(

                    id SERIAL PRIMARY KEY,

                    owner_id BIGINT
                        REFERENCES users(user_id)
                        ON DELETE CASCADE,

                    username TEXT UNIQUE,

                    bot_name TEXT,

                    is_active BOOLEAN DEFAULT TRUE,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                );
            """)

            # ================= ADMIN LOGS =================

            cur.execute("""
                CREATE TABLE IF NOT EXISTS admin_logs(

                    id SERIAL PRIMARY KEY,

                    admin_id BIGINT,

                    action TEXT,

                    target_id BIGINT,

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                );
            """)

        conn.commit()

    finally:
        conn.close()


# =====================================================
# USERS
# =====================================================

def add_user(user_id, username, first_name):
    conn = get_db()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO users(
                    user_id,
                    username,
                    first_name
                )

                VALUES(%s,%s,%s)

                ON CONFLICT(user_id)

                DO NOTHING
            """, (
                user_id,
                username,
                first_name
            ))

            cur.execute("""
                INSERT INTO balances(user_id)

                VALUES(%s)

                ON CONFLICT(user_id)

                DO NOTHING
            """, (user_id,))

        conn.commit()

    finally:
        conn.close()


def user_exists(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT 1

                FROM users

                WHERE user_id=%s

            """,(user_id,))

            return cur.fetchone() is not None

    finally:

        conn.close()


def get_user(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT *

                FROM users

                WHERE user_id=%s

            """,(user_id,))

            return cur.fetchone()

    finally:

        conn.close()
# =====================================================
# USER MANAGEMENT
# =====================================================

def ban_user(user_id):
    conn = get_db()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE users
                SET is_banned=TRUE
                WHERE user_id=%s
            """, (user_id,))

        conn.commit()

    finally:
        conn.close()


def unban_user(user_id):
    conn = get_db()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                UPDATE users
                SET is_banned=FALSE
                WHERE user_id=%s
            """, (user_id,))

        conn.commit()

    finally:
        conn.close()


def get_total_users():

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT COUNT(*)

                FROM users

            """)

            return cur.fetchone()[0]

    finally:

        conn.close()


# =====================================================
# BALANCE
# =====================================================

def get_balance(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT
                    deposit_balance,
                    earned_balance

                FROM balances

                WHERE user_id=%s

            """,(user_id,))

            row = cur.fetchone()

            if row:

                return {
                    "deposit": row[0],
                    "earned": row[1]
                }

            return {
                "deposit":0,
                "earned":0
            }

    finally:

        conn.close()


def get_deposit_balance(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT deposit_balance

                FROM balances

                WHERE user_id=%s

            """,(user_id,))

            row = cur.fetchone()

            if row:

                return row[0]

            return 0

    finally:

        conn.close()


def get_earned_balance(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT earned_balance

                FROM balances

                WHERE user_id=%s

            """,(user_id,))

            row = cur.fetchone()

            if row:

                return row[0]

            return 0

    finally:

        conn.close()


def add_deposit(user_id, amount):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                UPDATE balances

                SET deposit_balance =
                    deposit_balance + %s

                WHERE user_id=%s

            """,(amount,user_id))

        conn.commit()

    finally:

        conn.close()


def remove_deposit(user_id, amount):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                UPDATE balances

                SET deposit_balance =
                    deposit_balance - %s

                WHERE user_id=%s

            """,(amount,user_id))

        conn.commit()

    finally:

        conn.close()


def add_earned(user_id, amount):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                UPDATE balances

                SET earned_balance =
                    earned_balance + %s

                WHERE user_id=%s

            """,(amount,user_id))

        conn.commit()

    finally:

        conn.close()


def remove_earned(user_id, amount):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                UPDATE balances

                SET earned_balance =
                    earned_balance - %s

                WHERE user_id=%s

            """,(amount,user_id))

        conn.commit()

    finally:

        conn.close()
# =====================================================
# ADS FUNCTIONS
# =====================================================

def create_ad(user_id, link, ad_type, target_count):
    """
    Create a new advertisement.
    Reward = 0.27 Birr per completed task.
    Minimum target = 10 users.
    """

    if target_count < 10:
        return {
            "success": False,
            "message": "Minimum target is 10."
        }

    reward = 0.27
    total_price = reward * target_count

    conn = get_db()

    try:

        with conn.cursor() as cur:

            # Check deposit balance
            cur.execute("""
                SELECT deposit_balance
                FROM balances
                WHERE user_id=%s
            """, (user_id,))

            row = cur.fetchone()

            if row is None:
                return {
                    "success": False,
                    "message": "Balance account not found."
                }

            deposit = row[0]

            if deposit < total_price:
                return {
                    "success": False,
                    "message": "Insufficient deposit balance."
                }

            # Deduct deposit
            cur.execute("""
                UPDATE balances
                SET deposit_balance = deposit_balance - %s
                WHERE user_id=%s
            """, (total_price, user_id))

            # Create campaign
            cur.execute("""
                INSERT INTO ads(
                    user_id,
                    link,
                    type,
                    target_count,
                    current_count,
                    reward,
                    total_price,
                    status,
                    is_active
                )

                VALUES(
                    %s,%s,%s,%s,
                    0,
                    %s,
                    %s,
                    'active',
                    TRUE
                )

                RETURNING id
            """, (
                user_id,
                link,
                ad_type,
                target_count,
                reward,
                total_price
            ))

            ad_id = cur.fetchone()[0]

        conn.commit()

        return {
            "success": True,
            "ad_id": ad_id,
            "total_price": total_price
        }

    finally:
        conn.close()


def get_active_ads(ad_type):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    user_id,
                    link,
                    target_count,
                    current_count,
                    reward

                FROM ads

                WHERE
                    type=%s
                    AND is_active=TRUE
                    AND status='active'

                ORDER BY id ASC
            """, (ad_type,))

            return cur.fetchall()

    finally:

        conn.close()


def get_user_ads(user_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    link,
                    type,
                    target_count,
                    current_count,
                    status,
                    created_at

                FROM ads

                WHERE user_id=%s

                ORDER BY id DESC
            """, (user_id,))

            return cur.fetchall()

    finally:

        conn.close()


def get_ad(ad_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT *
                FROM ads
                WHERE id=%s
            """, (ad_id,))

            return cur.fetchone()

    finally:

        conn.close()


def delete_ad(ad_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                DELETE FROM ads
                WHERE id=%s
            """, (ad_id,))

        conn.commit()

    finally:

        conn.close()

# =====================================================
# AD PROGRESS
# =====================================================

def has_completed(user_id, ad_id):
    conn = get_db()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT 1
                FROM completed_ads
                WHERE user_id=%s
                AND ad_id=%s
            """, (user_id, ad_id))

            return cur.fetchone() is not None

    finally:
        conn.close()


def complete_ad(user_id, ad_id):

    conn = get_db()

    try:
        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO completed_ads(
                    user_id,
                    ad_id
                )

                VALUES(%s,%s)

                ON CONFLICT(user_id,ad_id)

                DO NOTHING
            """, (user_id, ad_id))

        conn.commit()

    finally:
        conn.close()


def increase_progress(ad_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                UPDATE ads

                SET current_count=current_count+1

                WHERE id=%s

                RETURNING
                    current_count,
                    target_count
            """, (ad_id,))

            row = cur.fetchone()

            if row is None:
                return False

            current = row[0]
            target = row[1]

            if current >= target:

                cur.execute("""
                    UPDATE ads

                    SET
                        status='completed',
                        is_active=FALSE,
                        completed_at=CURRENT_TIMESTAMP

                    WHERE id=%s
                """, (ad_id,))

        conn.commit()

        return True

    finally:

        conn.close()


def close_ad(ad_id):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                UPDATE ads

                SET
                    status='closed',
                    is_active=FALSE,
                    completed_at=CURRENT_TIMESTAMP

                WHERE id=%s
            """, (ad_id,))

        conn.commit()

    finally:

        conn.close()


# =====================================================
# VERIFICATION CODE
# =====================================================

def generate_code(length=8):

    letters = string.ascii_uppercase
    numbers = string.digits

    chars = letters + numbers

    return "".join(random.choice(chars) for _ in range(length))


def create_verification_code(user_id, ad_id):

    code = generate_code()

    expire = datetime.utcnow() + timedelta(minutes=10)

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""
                INSERT INTO verification_codes(

                    code,
                    ad_id,
                    user_id,
                    expires_at

                )

                VALUES(%s,%s,%s,%s)

            """, (
                code,
                ad_id,
                user_id,
                expire
            ))

        conn.commit()

        return code

    finally:

        conn.close()


def verify_code(code):

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT

                    id,
                    ad_id,
                    user_id,
                    used,
                    expires_at

                FROM verification_codes

                WHERE code=%s

            """, (code,))

            row = cur.fetchone()

            if row is None:
                return None

            if row[3]:
                return None

            if datetime.utcnow() > row[4]:
                return None

            cur.execute("""

                UPDATE verification_codes

                SET used=TRUE

                WHERE id=%s

            """, (row[0],))

        conn.commit()

        return {
            "ad_id": row[1],
            "user_id": row[2]
        }

    finally:

        conn.close()


# =====================================================
# STATISTICS
# =====================================================

def total_active_ads():

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT COUNT(*)

                FROM ads

                WHERE is_active=TRUE

            """)

            return cur.fetchone()[0]

    finally:

        conn.close()


def total_completed_ads():

    conn = get_db()

    try:

        with conn.cursor() as cur:

            cur.execute("""

                SELECT COUNT(*)

                FROM ads

                WHERE status='completed'

            """)

            return cur.fetchone()[0]

    finally:

        conn.close()