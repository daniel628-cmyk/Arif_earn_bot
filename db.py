import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    """Create and return database connection"""
    return psycopg.connect(DATABASE_URL)

def init_db():
    """Initialize all required tables"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # === Balances Table ===
            cur.execute("""
                CREATE TABLE IF NOT EXISTS balances(
                    user_id BIGINT PRIMARY KEY, 
                    deposit_balance FLOAT DEFAULT 0,
                    earned_balance FLOAT DEFAULT 0
                );
            """)

            # === Ads / Campaigns Table ===
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ads(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES balances(user_id),
                    link TEXT NOT NULL,
                    type TEXT CHECK (type IN ('channel', 'bot')),
                    target_count INT NOT NULL,
                    current_count INT DEFAULT 0,
                    price FLOAT NOT NULL,
                    status TEXT DEFAULT 'active',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # === Completed Tasks (prevent double earning) ===
            cur.execute("""
                CREATE TABLE IF NOT EXISTS completed_ads(
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    ad_id INT REFERENCES ads(id),
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, ad_id)
                );
            """)

            # === Bots Table (for Join Bots feature) ===
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bots(
                    id SERIAL PRIMARY KEY,
                    bot_name TEXT,
                    bot_username TEXT UNIQUE,
                    target_count INT DEFAULT 0,
                    current_count INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)

            # Optional: Channels table (if you still need it)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS channels(
                    id SERIAL PRIMARY KEY, 
                    channel_id BIGINT UNIQUE, 
                    channel_link TEXT, 
                    channel_name TEXT, 
                    is_active BOOLEAN DEFAULT TRUE, 
                    limit_count INT DEFAULT 0, 
                    current_count INT DEFAULT 0
                );
            """)

        conn.commit()
        print("✅ Database tables initialized successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
    finally:
        conn.close()


# Legacy function (kept for backward compatibility)
def update_and_check_limit(table_name, task_id):
    """Old function - consider using AdsManager instead"""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {table_name} SET current_count = current_count + 1 WHERE id = %s", (task_id,))
            cur.execute(f"SELECT current_count, limit_count FROM {table_name} WHERE id = %s", (task_id,))
            res = cur.fetchone()
            if res and res[0] >= res[1]:
                cur.execute(f"UPDATE {table_name} SET is_active = FALSE WHERE id = %s", (task_id,))
        conn.commit()
    finally:
        conn.close()