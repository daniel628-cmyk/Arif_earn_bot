import re
from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import get_db
from config import ADMIN_ID

router = Router()

class AdvertiseState(StatesGroup):
    waiting_for_link = State()
    waiting_for_members = State()

@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Channel", callback_data="adv_channel"),
         InlineKeyboardButton(text="🤖 Bot", callback_data="adv_bot")]
    ])
    await message.answer("📢 ምን ማስተዋወቅ ይፈልጋሉ?", reply_markup=kb)

@router.callback_query(F.data.startswith("adv_"))
async def get_ad_type(callback: CallbackQuery, state: FSMContext):
    adv_type = callback.data.split("_")[1]
    await state.update_data(type=adv_type)
    await callback.message.answer("🔗 ሊንኩን ይላኩ (ለቻናል @username፣ ለቦት ሊንክ):")
    await state.set_state(AdvertiseState.waiting_for_link)
    await callback.answer()

@router.message(AdvertiseState.waiting_for_link)
async def check_link(message: Message, state: FSMContext, bot: Bot):
    link = message.text.strip()
    try:
        # ለቻናልም ለቦትም ሊንኩ መኖሩን ያረጋግጣል
        await bot.get_chat(link)
        await state.update_data(link=link)
        await message.answer("💸 ስንት ሰው እንዲቀላቀሉ ይፈልጋሉ? (ቢያንስ 10 ሰው፣ ለአንድ ሰው 0.5 ብር)")
        await state.set_state