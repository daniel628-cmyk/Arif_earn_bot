from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import get_pool

router = Router()

@router.callback_query(F.data == "balance")
async def balance(call: CallbackQuery):

    pool = await get_pool()

    user = await pool.fetchrow(
        "SELECT balance FROM users WHERE user_id=$1",
        call.from_user.id
    )

    bal = user["balance"] if user else 0

    await call.message.answer(f"💰 Your Balance: {bal} Birr")
    await call.answer()


@router.callback_query(F.data == "ads")
async def ads(call: CallbackQuery):
    await call.message.answer("📢 Advertising system coming soon...")
    await call.answer()


@router.callback_query(F.data == "tasks")
async def tasks(call: CallbackQuery):
    await call.message.answer("📊 Tasks system coming soon...")
    await call.answer()