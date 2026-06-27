import os
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

conn = None


def connect_db():
    global conn

    conn = psycopg.connect(DATABASE_URL)

    print("✅ Database Connected")


def get_db():
    return conn


def init_db():

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        balance NUMERIC DEFAULT 0
    );
    """)

    conn.commit()

    cur.close()