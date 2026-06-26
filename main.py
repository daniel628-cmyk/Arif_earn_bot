import os
import psycopg2
import telebot
from telebot import types

# Variables ከ Railway Variables ይወሰዳሉ
TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN)

def get_db():
    # Neon/Postgres ለግንኙነት sslmode ይፈልጋል
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS channels (id SERIAL PRIMARY KEY, user_id BIGINT, channel_link TEXT)")
    conn.commit()
    cur.close()
    conn.close()

init_db()

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
    # ሊንኩን እና የላኪውን መረጃ በአግባቡ እንያዝ
    link = m.text
    user_id = m.chat.id
    
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO channels (user_id, channel_link) VALUES (%s, %s)", (user_id, link))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(m.chat.id, "✅ ቻናልዎ በተሳካ ሁኔታ ተመዝግቧል!")
    except Exception as e:
        bot.send_message(m.chat.id, f"⚠️ ስህተት ተፈጥሯል: {e}")

@bot.message_handler(func=lambda m: m.text == "👥 ቻናሎችን ተቀላቀል")
def view_channels(m):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT channel_link FROM channels ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
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