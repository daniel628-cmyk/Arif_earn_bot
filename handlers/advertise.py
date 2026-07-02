from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID
from ads_manager import AdsManager   # ← Import the manager we created

router = Router()

# Keyboards
def get_main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📢 Join Channels"), KeyboardButton(text="🤖 Join Bots")],
        [KeyboardButton(text="💰 Balance"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="📣 Advertise"), KeyboardButton(text="👥 Referrals")],
        [KeyboardButton(text="ℹ️ Info")]
    ], resize_keyboard=True)

def cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Cancel")]], resize_keyboard=True)

class AdvertiseState(StatesGroup):
    waiting_for_type = State()
    waiting_for_link = State()
    waiting_for_target = State()

@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Promote Channel", callback_data="adv_channel")],
        [InlineKeyboardButton(text="🤖 Promote Bot", callback_data="adv_bot")]
    ])
    await message.answer(
        "📢 What would you like to promote?", 
        reply_markup=kb
    )
    await state.set_state(AdvertiseState.waiting_for_type)

# Cancel at any time
@router.message(F.text == "❌ Cancel")
async def cancel_process(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Advertising process cancelled.", reply_markup=get_main_kb())

# Choose Type
@router.callback_query(F.data.startswith("adv_"))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    adv_type = callback.data.split("_")[1]  # "channel" or "bot"
    await state.update_data(type=adv_type)
    
    text = "🔗 Send your Channel username (e.g. @MyChannel)" if adv_type == "channel" else "🔗 Send your Bot username or link (e.g. @MyBot)"
    
    await callback.message.answer(text, reply_markup=cancel_kb())
    await state.set_state(AdvertiseState.waiting_for_link)
    await callback.answer()

# Link Validation
@router.message(AdvertiseState.waiting_for_link)
async def process_link(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Cancel":
        return await cancel_process(message, state)

    link = message.text.strip()
    if not link.startswith("@") and not link.startswith("https://t.me/"):
        link = "@" + link.lstrip("@")

    data = await state.get_data()
    adv_type = data.get("type")

    try:
        chat = await bot.get_chat(link)
        
        if adv_type == "channel":
            # Verify bot is admin in the channel
            member = await bot.get_chat_member(chat.id, bot.id)
            if member.status not in ["administrator", "creator"]:
                return await message.answer(
                    "❌ I am not an Administrator in this channel.\n\n"
                    "Please make me admin first, then try again.", 
                    reply_markup=cancel_kb()
                )

        await state.update_data(link=link, chat_id=chat.id)
        
        await message.answer(
            "👥 How many people do you want to reach?\n"
            "(Minimum 50 people. 1 person = 0.5 Birr)",
            reply_markup=cancel_kb()
        )
        await state.set_state(AdvertiseState.waiting_for_target)

    except Exception as e:
        await message.answer(
            "❌ Could not find this channel/bot.\n"
            "Make sure it is public and the username is correct.",
            reply_markup=cancel_kb()
        )

# Target Count + Payment
@router.message(AdvertiseState.waiting_for_target)
async def process_target(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ Cancel":
        return await cancel_process(message, state)

    if not message.text.isdigit():
        return await message.answer("❌ Please send a number only.", reply_markup=cancel_kb())

    target = int(message.text)
    if target < 50:
        return await message.answer("❌ Minimum target is 50 people.", reply_markup=cancel_kb())

    price = target * 0.5  # 0.5 Birr per person

    data = await state.get_data()
    user_id = message.from_user.id

    # Check balance
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT deposit_balance + earned_balance as total FROM balances WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        total_balance = row[0] if row else 0
    conn.close()

    if total_balance < price:
        await message.answer(
            f"⚠️ Insufficient balance!\n\n"
            f"Required: {price} Birr\n"
            f"Your balance: {total_balance} Birr\n\n"
            f"Please deposit and try again.\n"
            f"Contact Admin: @YourAdminUsername"
        )
        # Notify Admin
        try:
            await bot.send_message(
                ADMIN_ID,
                f"🚨 Low Balance Advertising Attempt\n\n"
                f"User: {message.from_user.full_name} (@{message.from_user.username})\n"
                f"Target: {target} people\n"
                f"Price: {price} Birr"
            )
        except:
            pass
        await state.clear()
        return

    # Create the ad
    result = AdsManager.create_ad(
        user_id=user_id,
        link=data['link'],
        target_count=target,
        ad_type=data['type'],
        price=price
    )

    if result["success"]:
        await message.answer(
            f"✅ Advertising campaign created successfully!\n\n"
            f"Link: {data['link']}\n"
            f"Target: {target} people\n"
            f"Cost: {price} Birr deducted from your balance.",
            reply_markup=get_main_kb()
        )
    else:
        await message.answer("❌ Failed to create campaign. Please try again.")

    await state.clear()