import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None

async def connect_db():
    global pool

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        statement_cache_size=0
    )

    print("✅ DB connected")


async def get_pool():
    return pool


async def init_db():
    global pool

    await pool.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        balance NUMERIC DEFAULT 0
    )
    """)