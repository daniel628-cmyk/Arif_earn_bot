from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

router = Router()

ADMIN_USERNAME = "Ariff_Support"

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

# ==================== USER WITHDRAW FLOW ====================

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

    # INSTANT DEDUCTION
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("UPDATE balances SET earned_balance = earned_balance - %s WHERE user_id = %s", (amount, user_id))
        conn.commit()
    conn.close()

    # Send to Admin
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
        f"✅ Amount has been deducted automatically.",
        reply_markup=kb
    )

    await message.answer(
        f"✅ Withdrawal Request Submitted!\n\n"
        f"💰 {amount} Birr has been deducted from your Earned Balance.\n"
        f"Status: **Pending Admin Approval**",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
        ])
    )

    await state.clear()


# ==================== ADMIN CALLBACK HANDLERS ====================

@router.callback_query(F.data.startswith("wd_approve_"))
async def approve_withdraw(callback: CallbackQuery, bot: Bot):
    try:
        _, _, user_id, amount = callback.data.split("_")
        user_id = int(user_id)
        amount = float(amount)

        await bot.send_message(
            user_id,
            f"✅ Your withdrawal request of **{amount} Birr** has been **Approved** by the admin.\n\n"
            f"💸 The payment has been processed to your Telebirr account.\n"
            f"Thank you for using our service!"
        )

        await callback.answer("✅ Approved successfully.", show_alert=True)
        await callback.message.edit_text(callback.message.text + "\n\n✅ **Approved**")

    except Exception:
        await callback.answer("Error while approving.")


@router.callback_query(F.data.startswith("wd_reject_"))
async def reject_withdraw(callback: CallbackQuery, bot: Bot):
    try:
        _, _, user_id, amount = callback.data.split("_")
        user_id = int(user_id)
        amount = float(amount)

        # Refund to earned balance
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("UPDATE balances SET earned_balance = earned_balance + %s WHERE user_id = %s", (amount, user_id))
            conn.commit()
        conn.close()

        await bot.send_message(
            user_id,
            f"❌ Your withdrawal request of **{amount} Birr** was **Rejected** by the admin.\n\n"
            f"The amount has been refunded back to your Earned Balance."
        )

        await callback.answer("❌ Rejected and refunded.", show_alert=True)
        await callback.message.edit_text(callback.message.text + "\n\n❌ **Rejected & Refunded**")

    except Exception:
        await callback.answer("Error while rejecting.")