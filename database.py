import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")

pool = None

async def connect_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ DB connected")

async def init_db():
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        balance NUMERIC DEFAULT 0
    )
    """)