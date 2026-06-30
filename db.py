import psycopg
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg.connect(DATABASE_URL)

def init_db():
    # ... (የቀድሞ ኮድህ) ...
    pass

def update_and_check_limit(table_name, task_id):
    conn = get_db()
    with conn.cursor() as cur:
        # ብዛቱን በ 1 ጨምር
        cur.execute(f"UPDATE {table_name} SET current_count = current_count + 1 WHERE id = %s", (task_id,))
        # ገደቡ ላይ መድረሱን አረጋግጥ
        cur.execute(f"SELECT current_count, limit_count FROM {table_name} WHERE id = %s", (task_id,))
        res = cur.fetchone()
        
        if res and res[0] >= res[1]: 
            cur.execute(f"UPDATE {table_name} SET is_active = FALSE WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()