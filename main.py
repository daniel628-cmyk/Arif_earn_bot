import os
import telebot
import psycopg2
from psycopg2 import pool
from telebot import types

# 1. Configuration
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN)

# Connection Pool መፍጠር (ይህ ቦትህ Crash እንዳያደርግ ይከላከላል)
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, DATABASE_URL, sslmode='require')
    print("Database pool created successfully.")
except Exception as e:
    print(f"Error creating connection pool: {e}")

# 2. የሰንጠረዦች መፍጠሪያ
def init_db():
    conn = db_pool.getconn()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS channels (id SERIAL PRIMARY KEY, user_id BIGINT, channel_link TEXT)")
    conn.commit()
    cur.close()
    db_pool.putconn(conn)

init_db()

# 3. Handlers
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 ቻናል አስተዋውቅ", "👥 ቻናሎችን ተቀላቀል")
    bot.send_message(m.chat.id, "እንኳን ደህና መጡ! ቻናል ለማስተዋወቅ ከታች ያለውን ይጫኑ።", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 ቻናል አስተዋውቅ")
def promote(m):
    msg = bot.send_message(m.chat.id, "እባክዎ የቻናልዎን ሊንክ ይላኩልኝ (ለምሳሌ: t.me/channelname):")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(m):
    link = m.text
    try:
        conn = db_pool.getconn()
        cur = conn.cursor()
        cur.execute("INSERT INTO channels (user_id, channel_link) VALUES (%s, %s)", (m.chat.id, link))
        conn.commit()
        cur.close()
        db_pool.putconn(conn)
        bot.send_message(m.chat.id, "✅ ቻናልዎ በተሳካ ሁኔታ ተመዝግቧል!")
    except Exception as e:
        bot.send_message(m.chat.id, "⚠️ ዳታቤዝ ስህተት: እንደገና ይሞክሩ።")

@bot.message_handler(func=lambda m: m.text == "👥 ቻናሎችን ተቀላቀል")
def view_channels(m):
    try:
        conn = db_pool.getconn()
        cur = conn.cursor()
        cur.execute("SELECT channel_link FROM channels ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        cur.close()
        db_pool.putconn(conn)
        
        if rows:
            text = "ለማስተዋወቅ የቀረቡ ቻናሎች:\n\n" + "\n".join([f"🔗 {row[0]}" for row in rows])
            bot.send_message(m.chat.id, text)
        else:
            bot.send_message(m.chat.id, "በአሁኑ ሰዓት ምንም ቻናል የለም።")
    except Exception as e:
        bot.send_message(m.chat.id, "⚠️ መረጃ መጫን አልተቻለም።")

if __name__ == '__main__':
    print("Bot is running...")
    bot.infinity_polling(none_stop=True)