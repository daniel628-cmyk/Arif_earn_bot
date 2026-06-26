import os
import psycopg2
import telebot
from telebot import types

# --- Configurations ---
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, threaded=False) # threaded=False ለሰርቨር የተረጋጋ ነው
ADMIN_ID = 5544893200  
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # sslmode='require' ለ Railway ግዴታ ነው
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, balance REAL DEFAULT 0.0, payout_balance REAL DEFAULT 0.0, invited_by BIGINT, phone_number TEXT)")
            cur.execute("CREATE TABLE IF NOT EXISTS tasks (task_id SERIAL PRIMARY KEY, title TEXT, link TEXT, reward REAL DEFAULT 1.0)")
            cur.execute("CREATE TABLE IF NOT EXISTS completed_tasks (user_id BIGINT, task_id INTEGER, PRIMARY KEY (user_id, task_id))")
            conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        if conn: conn.close()

init_db()

# --- Helpers ---
def get_user(uid):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT balance, payout_balance, invited_by, phone_number FROM users WHERE user_id = %s", (uid,))
            return cur.fetchone()
    except Exception as e:
        print(f"Get User Error: {e}")
    finally:
        if conn: conn.close()
    return None

def add_user(uid, ref=None):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id, invited_by) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (uid, ref))
            conn.commit()
    except Exception as e:
        print(f"Add User Error: {e}")
    finally:
        if conn: conn.close()

def update_phone(uid, phone):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET phone_number = %s WHERE user_id = %s", (phone, uid))
            conn.commit()
    except Exception as e:
        print(f"Update Phone Error: {e}")
    finally:
        if conn: conn.close()

# --- Handlers ---
@bot.message_handler(commands=['start'])
def start(m):
    try:
        uid = m.chat.id
        args = m.text.split()
        ref = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        add_user(uid, ref)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("👤 My Account", "📥 Withdraw")
        bot.send_message(uid, "እንኳን ደህና መጡ! 🌟", reply_markup=markup)
    except Exception as e:
        print(f"Start Error: {e}")

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account(m):
    data = get_user(m.chat.id)
    if data:
        bot.send_message(m.chat.id, f"💰 ሂሳብዎ: {data[0]} ብር\n📞 ስልክ: {data[3] or 'አልተመዘገበም'}")

@bot.message_handler(func=lambda m: m.text == "📥 Withdraw")
def withdraw(m):
    data = get_user(m.chat.id)
    if data and not data[3]:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(types.KeyboardButton("📱 ቁጥሬን ላክ", request_contact=True))
        bot.send_message(m.chat.id, "እባክዎ መጀመሪያ ስልክ ቁጥርዎን ያስመዝግቡ:", reply_markup=markup)
    else:
        bot.send_message(m.chat.id, "ሂሳብዎ ዝግጁ ነው፣ አድሚን ያነጋግሩ።")

@bot.message_handler(content_types=['contact'])
def phone(m):
    update_phone(m.chat.id, m.contact.phone_number)
    bot.send_message(m.chat.id, "✅ ስልክ ቁጥርዎ ተመዝግቧል!")

# --- Server Start ---
if __name__ == '__main__':
    print("Bot is starting...")
    bot.polling(none_stop=True, interval=0, timeout=20)
