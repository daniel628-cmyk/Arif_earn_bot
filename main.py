import os
import psycopg2
import telebot
from telebot import types

# Configurations
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN, threaded=False)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Database Initialization
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # ተጠቃሚዎች እና የማስተዋወቂያ ቻናሎቻቸው
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, balance REAL DEFAULT 0.0)")
    cur.execute("CREATE TABLE IF NOT EXISTS channels (id SERIAL PRIMARY KEY, user_id BIGINT, channel_link TEXT)")
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Handlers
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 ቻናል አስተዋውቅ", "👥 ቻናሎችን ተቀላቀል")
    bot.send_message(m.chat.id, "እንኳን ደህና መጡ! ይህ ቦት ቻናልዎን ለማስተዋወቅ ይረዳዎታል።", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 ቻናል አስተዋውቅ")
def promote(m):
    msg = bot.send_message(m.chat.id, "እባክዎ የቻናልዎን ሊንክ ይላኩልኝ:")
    bot.register_next_step_handler(msg, save_channel)

def save_channel(m):
    link = m.text
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO channels (user_id, channel_link) VALUES (%s, %s)", (m.chat.id, link))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(m.chat.id, "✅ ቻናልዎ ለሌሎች ተጠቃሚዎች እንዲታይ ተመዝግቧል!")

@bot.message_handler(func=lambda m: m.text == "👥 ቻናሎችን ተቀላቀል")
def view_channels(m):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT channel_link FROM channels ORDER BY id DESC LIMIT 5")
    channels = cur.fetchall()
    cur.close()
    conn.close()
    
    if channels:
        text = "ለማስተዋወቅ የቀረቡ ቻናሎች:\n\n" + "\n".join([c[0] for c in channels])
        bot.send_message(m.chat.id, text)
    else:
        bot.send_message(m.chat.id, "በአሁኑ ሰዓት ምንም ቻናል የለም።")

if __name__ == '__main__':
    bot.polling(none_stop=True)