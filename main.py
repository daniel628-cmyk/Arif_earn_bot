import psycopg2
import telebot
from telebot import types

# --- 1. ቶከን እና ዳታቤዝ (እዚህ ቀጥታ አስገባ) ---
TOKEN = "8315001763:AAFv4xMCN3Li2Gu2aFe2-girlnRlYNoghyc"
DATABASE_URL = "postgresql://postgres:ArifBot3991&@db.qvhexkdafndccprpqlit.supabase.co:5432/postgres"

bot = telebot.TeleBot(TOKEN, threaded=False)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- 2. Database Setup ---
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, balance REAL DEFAULT 0.0)")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Setup Error: {e}")

init_db()

# --- 3. Bot Handlers ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👤 My Account", "📥 Withdraw")
    bot.send_message(m.chat.id, "ሰላም! ቦቱ አሁን በትክክል እየሰራ ነው።", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def account(m):
    bot.send_message(m.chat.id, "እንኳን ደህና መጡ! ሂሳብዎ 0.0 ብር ነው።")

# --- 4. Start Bot ---
if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)