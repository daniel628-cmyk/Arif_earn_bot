import os
import psycopg2
import telebot
from telebot import types

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 5544893200
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- Main Menu (Inline) ---
def get_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("👤 መለያዬ (Account)", callback_data="account"),
        types.InlineKeyboardButton("📢 ስራዎች (Tasks)", callback_data="tasks"),
        types.InlineKeyboardButton("🔗 መጋበዣ (Referral)", callback_data="referral"),
        types.InlineKeyboardButton("📥 ክፍያ መጠየቅ (Withdraw)", callback_data="withdraw"),
        types.InlineKeyboardButton("🚀 ማስታወቂያ (Advertising)", callback_data="promote")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    add_user(m.chat.id)
    bot.send_message(m.chat.id, "🌟 ወደ Arif Earn በደህና መጡ! የሚፈልጉትን ይምረጡ፦", reply_markup=get_main_markup())

# --- Callback Handlers ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "account":
        data = get_user(call.message.chat.id)
        bot.edit_message_text(f"📋 **መረጃዎ**:\n💰 ሂሳብ: {data[1]} ብር\n👥 የጋበዙት: 0", 
                              call.message.chat.id, call.message.message_id, reply_markup=get_main_markup())
    
    elif call.data == "tasks":
        bot.edit_message_text("📢 **አሁን የሚገኙ ስራዎች**:\n(እዚህ ጋር ከ Database Task ይዘረዘራል)", 
                              call.message.chat.id, call.message.message_id, reply_markup=get_main_markup())
    
    elif call.data == "referral":
        link = f"https://t.me/{bot.get_me().username}?start={call.message.chat.id}"
        bot.edit_message_text(f"🔗 **የእርስዎ መጋበዣ ሊንክ**:\n`{link}`\n\nለእያንዳንዱ ሰው 3 ብር ያገኛሉ!", 
                              call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=get_main_markup())
    
    elif call.data == "withdraw":
        bot.edit_message_text("📥 **ክፍያ መጠየቂያ**:\nቢያንስ 25 ብር መኖር አለበት። ቁጥርዎን ይላኩ።", 
                              call.message.chat.id, call.message.message_id, reply_markup=get_main_markup())
    
    elif call.data == "promote":
        bot.edit_message_text("🚀 **ማስታወቂያ ለማሰራት**:\nቻናልዎን ለማስተዋወቅ አድሚኑን ያነጋግሩ @th_ug_life", 
                              call.message.chat.id, call.message.message_id, reply_markup=get_main_markup())

# --- Database Mockup (ለአጭር ማሳያ) ---
def add_user(uid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
    conn.commit()
    conn.close()

def get_user(uid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, balance FROM users WHERE user_id = %s", (uid,))
    res = cur.fetchone()
    conn.close()
    return res or (uid, 0.0)

if __name__ == '__main__':
    bot.infinity_polling()
