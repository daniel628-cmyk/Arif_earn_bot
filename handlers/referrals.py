from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from db import get_db

router = Router()

@router.message(Command("start"))
async def start_with_referral(message: Message):
    args = message.text.split()
    referrer_id = None

    if len(args) > 1 and args[1].isdigit():
        referrer_id = int(args[1])

    user_id = message.from_user.id

    # Register user if new
    conn = get_db()
    with conn.cursor() as cur:
        # Create balance if not exists
        cur.execute("""
            INSERT INTO balances (user_id, deposit_balance, earned_balance)
            VALUES (%s, 0, 0)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))

        if referrer_id and referrer_id != user_id:
            # Check if this referral already exists
            cur.execute("SELECT 1 FROM referrals WHERE referred_id = %s", (user_id,))
            if not cur.fetchone():
                # Record referral
                cur.execute("""
                    INSERT INTO referrals (referrer_id, referred_id, reward_given)
                    VALUES (%s, %s, FALSE)
                """, (referrer_id, user_id))
                
                # Give reward to referrer
                cur.execute("""
                    UPDATE balances 
                    SET earned_balance = earned_balance + 0.50 
                    WHERE user_id = %s
                """, (referrer_id,))
                
                # Mark reward as given
                cur.execute("UPDATE referrals SET reward_given = TRUE WHERE referred_id = %s", (user_id,))
                
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
    conn.close()

    # Normal start message
    await message.answer(
        "👋 Welcome to Mela Earning Bot!\n\n"
        "Invite friends and earn 0.50 Birr per referral.\n"
        "Use the menu below:",
        reply_markup=get_main_kb()
    )


@router.message(F.text == "👥 Referrals")
async def show_referral(message: Message):
    user_id = message.from_user.id
    bot_username = (await message.bot.get_me()).username

    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = %s", (user_id,))
        referral_count = cur.fetchone()[0]
    conn.close()

    await message.answer(
        f"👥 **Your Referral System**\n\n"
        f"🔗 Your Referral Link:\n"
        f"`{referral_link}`\n\n"
        f"📊 Total Referrals: **{referral_count}**\n"
        f"💰 Reward per referral: **0.50 Birr**\n\n"
        f"Share this link with your friends!",
        parse_mode="Markdown"
    )