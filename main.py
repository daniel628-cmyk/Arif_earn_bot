import os
import psycopg2
import telebot
from telebot import types
import time

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
ADMIN_ID = 5544893200  
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    balance REAL DEFAULT 0.0,
                    payout_balance REAL DEFAULT 0.0,
                    invited_by BIGINT,
                    phone_number TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id SERIAL PRIMARY KEY,
                    title TEXT,
                    link TEXT,
                    reward REAL DEFAULT 1.0
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS completed_tasks (
                    user_id BIGINT,
                    task_id INTEGER,
                    PRIMARY KEY (user_id, task_id)
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"Database init error: {e}")
    finally:
        if conn:
            conn.close()

init_db()

def get_user(user_id):
    conn = None
    res = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT balance, payout_balance, invited_by, phone_number FROM users WHERE user_id = %s", (user_id,))
            res = cursor.fetchone()
    except Exception as e:
        print(f"get_user Error: {e}")
    finally:
        if conn:
            conn.close()
    return res

def add_user(user_id, referrer_id=None):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (user_id, referrer_id))
            conn.commit()
    except Exception as e:
        print(f"add_user Error: {e}")
    finally:
        if conn:
            conn.close()

def update_phone(user_id, phone):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET phone_number = %s WHERE user_id = %s", (phone, user_id))
            conn.commit()
    except Exception as e:
        print(f"update_phone Error: {e}")
    finally:
        if conn:
            conn.close()

def add_reward(user_id, amount):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET balance = balance + %s, payout_balance = payout_balance + %s WHERE user_id = %s", (amount, amount, user_id))
            conn.commit()
    except Exception as e:
        print(f"add_reward Error: {e}")
    finally:
        if conn:
            conn.close()

def request_withdrawal(user_id, amount):
    conn = None
    success = False
    phone = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT payout_balance, phone_number FROM users WHERE user_id = %s", (user_id,))
            res = cursor.fetchone()
            if res and res[0] >= amount and res[1] is not None:
                cursor.execute("UPDATE users SET payout_balance = payout_balance - %s WHERE user_id = %s", (amount, user_id))
                conn.commit()
                success = True
                phone = res[1]
    except Exception as e:
        print(f"request_withdrawal Error: {e}")
    finally:
        if conn:
            conn.close()
    return success, phone

def add_new_task(title, link, reward):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO tasks (title, link, reward) VALUES (%s, %s, %s)", (title, link, reward))
            conn.commit()
    except Exception as e:
        print(f"add_new_task Error: {e}")
    finally:
        if conn:
            conn.close()

def get_available_task(user_id):
    conn = None
    res = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT task_id, title, link, reward FROM tasks 
                WHERE task_id NOT IN (SELECT task_id FROM completed_tasks WHERE user_id = %s)
                LIMIT 1
            ''', (user_id,))
            res = cursor.fetchone()
    except Exception as e:
        print(f"get_available_task Error: {e}")
    finally:
        if conn:
            conn.close()
    return res

def mark_task_completed(user_id, task_id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO completed_tasks (user_id, task_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, task_id))
            conn.commit()
    except Exception as e:
        print(f"mark_task_completed Error: {e}")
    finally:
        if conn:
            conn.close()

def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👤 My Account")
    btn2 = types.KeyboardButton("🔗 Invite Link")
    btn3 = types.KeyboardButton("📥 Withdraw")
    btn4 = types.KeyboardButton("📢 Join Channels")
    btn5 = types.KeyboardButton("🚀 Promote (ማስታወቂያ)")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    start_args = message.text.split()
    referrer_id = None
    if len(start_args) > 1 and start_args[1].isdigit():
        referrer_id = int(start_args[1])
        if referrer_id == user_id:
            referrer_id = None
    try:
        user_exists = get_user(user_id)
        if not user_exists:
            add_user(user_id, referrer_id)
            if referrer_id:
                add_reward(referrer_id, 3.0)
                try:
                    bot.send_message(referrer_id, f"🎉 **አዲስ ሰው ጋብዘዋል!**\n👤 {user_name} በእርስዎ ሊንክ ገብቷል። **3.00 ብር** ተጨምሯል።", parse_mode='Markdown')
                except Exception:
                    pass
    except Exception as e:
        print(f"Error in start: {e}")
    welcome_text = (
        f"🌟 👋 **እንኳን ወደ {bot.get_me().first_name} በደህና መጡ!** 🌟\n\n"
        "ይህ ቦት ቻናሎችን እና ቦቶችን Join በማድረግ እንዲሁም ጓደኞችዎን በመጋበዝ "
        "በቀላሉ ገቢ የሚያገኙበት ታማኝ መድረክ ነው! 💰\n\n"
        "📌 **ለመጀመር ከታች ያሉትን ቁልፎች ይጠቀሙ፦**"
    )
    bot.send_message(user_id, welcome_text, parse_mode='Markdown', reply_markup=main_menu_keyboard())

@bot.message_handler(func=lambda m: m.text == "👤 My Account")
def my_account(message):
    user_id = message.chat.id
    user_data = get_user(user_id)
    if user_data:
        balance, payout_balance, _, phone = user_data
        phone_status = phone if phone else "አልተመዘገበም ❌"
        account_text = (
            "📋 **የአካውንትዎ መረጃ (My Account)**\n\n"
            f"👤 የተጠቃሚ ID: `{user_id}`\n"
            f"📞 የቴሌብር ቁጥር: `{phone_status}`\n\n"
            f"💰 አጠቃላይ የሰሩት: **{balance:.2f} ብር**\n"
            f"📥 ማውጣት የሚችሉት ቀሪ ሂሳብ: **{payout_balance:.2f} ብር**"
        )
        bot.send_message(user_id, account_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "🔗 Invite Link")
def invite_link(message):
    user_id = message.chat.id
    bot_username = bot.get_me().username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    invite_text = (
        "🔗 **የመጋበዣ ሊንክዎ (Your Referral Link)**\n\n"
        "👥 ለእያንዳንዱ ለሚጋብዙት ሰው: **3.00 ብር** ያገኛሉ።\n\n"
        f"👇 የእርስዎ ሊንክ ይህ ነው፦\n`{referral_link}`"
    )
    bot.send_message(user_id, invite_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📢 Join Channels")
def join_channels(message):
    user_id = message.chat.id
    task = get_available_task(user_id)
    if task:
        task_id, title, link, reward = task
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton(f"🔗 {title}ን ለመቀላቀል ይጫኑ", url=link)
        btn_check = types.InlineKeyboardButton("✅ አረጋግጥ (Verify)", callback_data=f"check_{task_id}_{reward}")
        markup.add(btn_link)
        markup.add(btn_check)
        task_text = (
            "📢 **አዲስ ማስታወቂያ (Task) ወጥቷል!**\n\n"
            "ከታች ያለውን ሊንክ ተጭነው ቻናሉን ወይም ቦቱን ይቀላቀሉ (Join ያድርጉ)።\n"
            f"💰 የዚህ ስራ ክፍያ፦ **{reward:.2f} ብር**"
        )
        bot.send_message(user_id, task_text, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(user_id, "🔄 **በአሁኑ ሰዓት አዳዲስ ስራዎች አልተዘጋጁም።**")

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def verify_task(call):
    user_id = call.message.chat.id
    _, task_id, reward = call.data.split("_")
    task_id = int(task_id)
    reward = float(reward)
    try:
        mark_task_completed(user_id, task_id)
        add_reward(user_id, reward)
        bot.answer_callback_query(call.id, "✅ ስራው ጸድቋል!")
        bot.edit_message_text(f"🎉 **እንኳን ደስ አለዎት!**\n**{reward:.2f} ብር** ወደ አካውንትዎ ተጨምሯል!", chat_id=user_id, message_id=call.message.message_id, parse_mode='Markdown')
    except Exception:
        bot.answer_callback_query(call.id, "❌ ስህተት ተፈጥሯል!")

@bot.message_handler(func=lambda m: m.text == "🚀 Promote (ማስታወቂያ)")
def promote_panel(message):
    promote_text = "🚀 **የእርስዎን ቻናል ማስተዋወቅ ይፈልጋሉ?**\n\n👇 አድሚኑን ያነጋግሩ፦\n👉 @th_ug_life"
    bot.send_message(message.chat.id, promote_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📥 Withdraw")
def process_withdraw(message):
    user_id = message.chat.id
    user_data = get_user(user_id)
    if user_data:
        _, payout_balance, _, phone = user_data
        if not phone:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            btn_phone = types.KeyboardButton("📱 የቴሌብር ስልክ ቁጥሬን ላክ", request_contact=True)
            markup.add(btn_phone)
            bot.send_message(user_id, "⚠️ እባክዎ መጀመሪያ የቴሌብር ስልክ ቁጥርዎን ለመመዝገብ ከታች ያለውን ቁልፍ ይጫኑ፡", reply_markup=markup)
            return
        MIN_WITHDRAW = 25.0
        if payout_balance < MIN_WITHDRAW:
            bot.send_message(user_id, f"❌ **ማውጣት የሚችሉት አነስተኛው የብር መጠን {MIN_WITHDRAW} ብር ነው።**\nየእርስዎ ቀሪ ሂሳብ፦ {payout_balance:.2f} ብር ነው።")
        else:
            msg = bot.send_message(user_id, f"💰 ማውጣት የሚችሉት መጠን: **{payout_balance:.2f} ብር**\n\nእባክዎ መጠን በቁጥር ብቻ ይጻፉልኝ (ምሳሌ: 50)።", parse_mode='Markdown')
            bot.register_next_step_handler(msg, handle_withdraw_amount)

@bot.message_handler(content_types=['contact'])
def save_phone(message):
    user_id = message.chat.id
    if message.contact:
        phone = message.contact.phone_number
        update_phone(user_id, phone)
        bot.send_message(user_id, f"✅ የቴሌብር ስልክ ቁጥርዎ (`{phone}`) ተመዝግቧል!", parse_mode='Markdown', reply_markup=main_menu_keyboard())

def handle_withdraw_amount(message):
    user_id = message.chat.id
    amount_text = message.text
    if not amount_text.isdigit():
        bot.send_message(user_id, "❌ እባክዎ መጠን በቁጥር ብቻ ያስገቡ!", reply_markup=main_menu_keyboard())
        return
    amount = float(amount_text)
    success, phone = request_withdrawal(user_id, amount)
    if success:
        bot.send_message(user_id, "✅ **የክፍያ ጥያቄዎ በተሳካ ሁኔታ ለአድሚን ተልኳል!**", reply_markup=main_menu_keyboard())
        admin_text = f"🚨 **አዲስ የክፍያ ጥያቄ!**\n\n👤 ID: `{user_id}`\n📞 ስልክ: `{phone}`\n💰 መጠን: **{amount} ብር**"
        bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ ስህተት ተፈጥሯል! በቂ ገንዘብ እንዳለዎት ያረጋግጡ።", reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['add_task'])
def admin_add_task(message):
    if message.chat.id == ADMIN_ID:
        try:
            parts = message.text.replace("/add_task", "").split("|")
            title = parts[0].strip()
            link = parts[1].strip()
            reward = float(parts[2].strip())
            add_new_task(title, link, reward)
            bot.send_message(ADMIN_ID, f"✅ **አዲስ ስራ ተለቋል!**\n📌 ስም: {title}\n💰 ክፍያ: {reward} ብር")
        except Exception:
            bot.send_message(ADMIN_ID, "❌ አጠቃቀም፦ `/add_task ስም | ሊንክ | ክፍያ`")

if __name__ == '__main__':
    try:
        bot.delete_webhook()
        time.sleep(1)
    except Exception:
        pass
    print("Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
