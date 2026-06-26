import os
import psycopg2
import telebot
from telebot import types

# ቶከን እና ዳታቤዝ ከ Railway Environment Variables እንዲያነቡ ይደረጋል
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN, threaded=False)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Database Initialization
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, balance REAL DEFAULT 0.0)")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

init_db()

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "✅ ቦቱ ተነሳ! አሁን ደህንነቱ በተጠበቀ ሁኔታ እየሰራ ነው።")

if __name__ == '__main__':
    print("Bot is running...")
    bot.polling(none_stop=True)