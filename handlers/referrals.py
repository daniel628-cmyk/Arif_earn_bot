from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from db import get_db

router = Router()

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)


@router.message(F.text == "👥 Referrals")
async def show_referrals(message: Message):
    user_id = message.from_user.id
    bot_username = (await message.bot.get_me()).username

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = %s", (user_id,))
        total_referrals = cur.fetchone()[0]
    conn.close()

    await message.answer(
        f"👥 **Referral System**\n\n"
        f"🔗 Your Referral Link:\n"
        f"`{referral_link}`\n\n"
        f"📊 Total Referrals: **{total_referrals}**\n"
        f"💰 Reward per referral: **0.50 Birr**\n\n"
        f"Share this link with friends and earn money every time they join!",
        parse_mode="Markdown",
        reply_markup=get_main_kb()
    )


# This should be merged with your /start command in handlers/start.py
@router.message(Command("start"))
async def start_handler(message: Message):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])

    user_id = message.from_user.id

    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Create balance record if new user
            cur.execute("""
                INSERT INTO balances (user_id, deposit_balance, earned_balance)
                VALUES (%s, 0, 0)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id,))

            # Process referral
            if referrer_id and referrer_id != user_id:
                cur.execute("SELECT 1 FROM referrals WHERE referred_id = %s", (user_id,))
                if not cur.fetchone():
                    # Give reward to referrer
                    cur.execute("""
                        UPDATE balances 
                        SET earned_balance = earned_balance + 0.50 
                        WHERE user_id = %s
                    """, (referrer_id,))

                    # Record the referral
                    cur.execute("""
                        INSERT INTO referrals (referrer_id, referred_id, reward_given)
                        VALUES (%s, %s, TRUE)
                    """, (referferrer_id, user_id))

                    # Notify referrer
                    try:
                        await message.bot.send_message(
                            referrer_id,
                            f"🎉 New referral!\n"
                            f"Someone joined using your link.\n"
                            f"+0.50 Birr added to your Earned Balance!"
                        )
                    except:
                        pass

        conn.commit()

    except Exception as e:
        print(f"Referral error: {e}")
    finally:
        conn.close()

    await message.answer(
        "👋 Welcome to **Mela Earning Bot**!\n\n"
        "Complete tasks, invite friends, and earn money.\n"
        "Use the buttons below to get started:",
        reply_markup=get_main_kb()
    )