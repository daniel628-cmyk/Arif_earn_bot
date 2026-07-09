from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from ads_manager import AdsManager
from db import get_balance

router = Router()


# ==========================
# STATES
# ==========================

class AdvertiseState(StatesGroup):
    waiting_type = State()
    waiting_link = State()
    waiting_target = State()


# ==========================
# ADVERTISE MENU
# ==========================

@router.message(F.text == "📢 Advertise")
async def advertise_menu(message: Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Channel Advertisement",
                    callback_data="ad_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Bot Advertisement",
                    callback_data="ad_bot"
                )
            ]
        ]
    )

    balance = get_balance(message.from_user.id)

    text = (
        "📢 <b>Create Advertisement</b>\n\n"
        f"💳 Deposit Balance: <b>{balance['deposit']:.2f} Birr</b>\n\n"
        "💰 Reward Per User: <b>0.5 Birr</b>\n"
        "👥 Minimum Target: <b>10 Users</b>\n\n"
        "Select advertisement type."
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ==========================
# SELECT TYPE
# ==========================

@router.callback_query(F.data == "ad_channel")
async def channel_selected(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        ad_type="channel"
    )

    await state.set_state(
        AdvertiseState.waiting_link
    )

    await callback.message.answer(
        "📢 Send your channel username.\n\nExample:\n@MyChannel"
    )

    await callback.answer()


@router.callback_query(F.data == "ad_bot")
async def bot_selected(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.update_data(
        ad_type="bot"
    )

    await state.set_state(
        AdvertiseState.waiting_link
    )

    await callback.message.answer(
        "🤖 Send your bot username.\n\nExample:\n@MyAwesomeBot"
    )

    await callback.answer()
from config import ADMIN_USERNAME


# ==========================
# RECEIVE LINK
# ==========================

@router.message(AdvertiseState.waiting_link)
async def receive_link(
    message: Message,
    state: FSMContext
):

    link = message.text.strip()

    if not link.startswith("@"):
        return await message.answer(
            "❌ Invalid username.\n\nExample:\n@MyChannel"
        )

    await state.update_data(link=link)

    await state.set_state(
        AdvertiseState.waiting_target
    )

    await message.answer(
        "👥 Send target users.\n\n"
        "Minimum: 10"
    )


# ==========================
# RECEIVE TARGET
# ==========================

@router.message(AdvertiseState.waiting_target)
async def receive_target(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():
        return await message.answer(
            "❌ Target must be a number."
        )

    target = int(message.text)

    if target < 10:
        return await message.answer(
            "❌ Minimum target is 10 users."
        )

    data = await state.get_data()

    ad_type = data["ad_type"]
    link = data["link"]

    total_price = target * 0.5

    balance = get_balance(
        message.from_user.id
    )

    if balance["deposit"] < total_price:

        await state.clear()

        return await message.answer(

            f"❌ Your deposit balance is insufficient.\n\n"

            f"💰 Required: {total_price:.2f} Birr\n"

            f"💳 Your Balance: {balance['deposit']:.2f} Birr\n\n"

            f"Please deposit using:\n"

            f"@{ADMIN_USERNAME}"

        )

    result = AdsManager.create_campaign(

        user_id=message.from_user.id,

        link=link,

        ad_type=ad_type,

        target=target

    )

    await state.clear()

    if not result["success"]:

        return await message.answer(
            result["message"]
        )

    await message.answer(

        "✅ Advertisement created successfully!\n\n"

        f"🆔 Campaign ID: {result['ad_id']}\n"

        f"🔗 Link: {link}\n"

        f"👥 Target: {target}\n"

        f"💰 Cost: {result['total_price']:.2f} Birr\n"

        "📢 Your campaign is now active."

    )
# ==========================
# MY ADVERTISEMENTS
# ==========================

@router.message(F.text == "📋 My Advertisements")
async def my_advertisements(message: Message):

    ads = AdsManager.my_ads(message.from_user.id)

    if not ads:
        return await message.answer(
            "📭 You don't have any advertisements."
        )

    for ad in ads:

        ad_id = ad[0]
        link = ad[1]
        ad_type = ad[2]
        target = ad[3]
        current = ad[4]
        status = ad[5]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📊 Progress",
                        callback_data=f"progress_{ad_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Delete",
                        callback_data=f"delete_{ad_id}"
                    ),
                    InlineKeyboardButton(
                        text="🔒 Close",
                        callback_data=f"close_{ad_id}"
                    )
                ]
            ]
        )

        await message.answer(

            f"🆔 ID : {ad_id}\n"
            f"📢 Type : {ad_type.title()}\n"
            f"🔗 {link}\n"
            f"👥 {current}/{target}\n"
            f"📌 Status : {status.title()}",

            reply_markup=keyboard

        )


# ==========================
# PROGRESS
# ==========================

@router.callback_query(F.data.startswith("progress_"))
async def progress_callback(callback: CallbackQuery):

    ad_id = int(callback.data.split("_")[1])

    info = AdsManager.campaign_info(ad_id)

    if info is None:
        return await callback.answer(
            "Advertisement not found.",
            show_alert=True
        )

    remain = info["target"] - info["current"]

    await callback.message.answer(

        "📊 Advertisement Progress\n\n"

        f"🆔 ID : {info['id']}\n"

        f"📢 Type : {info['type'].title()}\n"

        f"🔗 {info['link']}\n\n"

        f"👥 Progress : {info['current']}/{info['target']}\n"

        f"⌛ Remaining : {remain}\n"

        f"📌 Status : {info['status'].title()}"

    )

    await callback.answer()


# ==========================
# DELETE ADVERTISEMENT
# ==========================

@router.callback_query(F.data.startswith("delete_"))
async def delete_callback(callback: CallbackQuery):

    ad_id = int(callback.data.split("_")[1])

    result = AdsManager.delete_campaign(ad_id)

    if result["success"]:

        await callback.message.edit_text(
            "🗑 Advertisement deleted successfully."
        )

    else:

        await callback.answer(
            result["message"],
            show_alert=True
        )


# ==========================
# CLOSE ADVERTISEMENT
# ==========================

@router.callback_query(F.data.startswith("close_"))
async def close_callback(callback: CallbackQuery):

    ad_id = int(callback.data.split("_")[1])

    result = AdsManager.admin_close(ad_id)

    if result["success"]:

        await callback.message.edit_text(
            "🔒 Advertisement closed successfully."
        )

    else:

        await callback.answer(
            result["message"],
            show_alert=True
        )