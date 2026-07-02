from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

router = Router()

ADMIN_USERNAME = "Ariff_Support"   # ← Your admin username

class WithdrawState(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()

def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)

@router.message(F.text == "💸 Withdraw")
async def start_withdraw(message: Message, state: FSMContext):
    user_id = message.from_user.id

    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT earned_balance FROM balances WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        earned = float(row[0]) if row else 0.0
    conn.close()

    if earned < 25:
        await message.answer(
            "❌ Withdrawal Denied\n\n"
            "• Minimum withdrawal amount is **25 Birr**\n"
            "• You can only withdraw from your **Earned Balance**"
        )
        return

    await state.update_data(earned=earned, amount=25.0)
    await message.answer(
        "🔄 Withdrawal Request Started\n\n"
        "Please send your **Telebirr Phone Number** (e.g. 0912345678):",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Cancel")]], resize_keyboard=True)
    )
    await state.set_state(WithdrawState.waiting_for_phone)


@router.message(WithdrawState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text == "❌ Cancel":
        await state.clear()
        return await message.answer("✅ Cancelled.", reply_markup=get_main_kb())

    phone = message.text.strip()
    if not (phone.isdigit() and len(phone) == 10 and phone.startswith(("09", "07"))):
        return await message.answer("❌ Invalid Telebirr number.\nIt must be 10 digits and start with 09 or 07.")

    await state.update_data(phone=phone)
    await message.answer("✅ Please send your **Full Name** (as registered on Telebirr):")
    await state.set_state(WithdrawState.waiting_for_name)


@router.message(WithdrawState.waiting_for_name)
async def process_name(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Cancel":
        await state.clear()
        return await message.answer("✅ Cancelled.", reply_markup=get_main_kb())

    data = await state.get_data()
    user_id = message.from_user.id
    name = message.text.strip()
    amount = data['amount']

    # === INSTANT DEDUCTION FROM EARNED BALANCE ===
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE balances 
            SET earned_balance = earned_balance - %s 
            WHERE user_id = %s
        """, (amount, user_id))
        conn.commit()
    conn.close()

    # Admin Notification with Action Buttons
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"wd_approve_{user_id}_{amount}"),
            InlineKeyboardButton(text="❌ Reject & Refund", callback_data=f"wd_reject_{user_id}_{amount}")
        ]
    ])

    await bot.send_message(
        ADMIN_ID,
        f"🚨 **New Withdrawal Request**\n\n"
        f"👤 User: {message.from_user.full_name}\n"
        f"📎 @{message.from_user.username or 'N/A'}\n"
        f"🆔 {user_id}\n\n"
        f"💰 Amount: {amount} Birr\n"
        f"📱 Telebirr: {data['phone']}\n"
        f"👨 Name: {name}\n\n"
        f"✅ Amount has been deducted from Earned Balance.",
        reply_markup=kb
    )

    await message.answer(
        f"✅ Withdrawal Request Submitted!\n\n"
        f"💰 {amount} Birr has been deducted from your Earned Balance.\n"
        f"Status: **Pending Admin Approval**\n\n"
        f"If you have any questions, contact the admin:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
        ])
    )

    await state.clear()