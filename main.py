import os
import psycopg2
import telebot
from telebot import types

TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN)

def get_db_connection():
    # sslmode='require' ለ Railway ግዴታ ነው
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Database Initialization
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, balance REAL DEFAULT 0.0)")
        cur.execute("CREATE TABLE IF NOT EXISTS channels (id SERIAL PRIMARY KEY, user_id BIGINT, channel_link TEXT)")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

init_db()

@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 ቻናል አስተዋውቅ", "👥 ቻናሎችን ተቀላቀል")
    bot.send_message(m.chat.id, "እንኳን ደህና መጡ! ቻናልዎን ለማስተዋወቅ ዝግጁ ነን።", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 ቻናል አስተዋውቅ")
def promote(m):
    msg = bot.send_message(m.chat.id, "እባክዎ የቻናልዎን ሊንክ ይላኩልኝ:")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(m):
    link = m.text
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO channels (user_id, channel_link) VALUES (%s, %s)", (m.chat.id, link))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(m.chat.id, "✅ ቻናልዎ በተሳካ ሁኔታ ተመዝግቧል!")
    except Exception as e:
        print(f"Save Channel Error: {e}")
        bot.send_message(m.chat.id, "⚠️ ይቅርታ፣ ዳታቤዝ ላይ ስህተት ተፈጥሯል፣ እንደገና ይሞክሩ።")

@bot.message_handler(func=lambda m: m.text == "👥 ቻናሎችን ተቀላቀል")
def view_channels(m):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT channel_link FROM channels ORDER BY id DESC LIMIT 5")
        channels = cur.fetchall()
        cur.close()
        conn.close()
        
        if channels:
            text = "ለማስተዋወቅ የቀረቡ ቻናሎች:\n\n" + "\n".join([f"🔗 {c[0]}" for c in channels])
            bot.send_message(m.chat.id, text)
        else:
            bot.send_message(m.chat.id, "በአሁኑ ሰዓት ምንም ቻናል የለም።")
    except Exception as e:
        print(f"View Channels Error: {e}")
        bot.send_message(m.chat.id, "⚠️ ዳታቤዝ ሊገናኝ አልቻለም።")

if __name__ == '__main__':
    bot.infinity_polling(none_stop=True, interval=0, timeout=20)