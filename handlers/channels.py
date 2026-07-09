from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from ads_manager import AdsManager

router = Router()

REWARD = 0.27


@router.message(F.text == "📢 Join Channels")
async def join_channels(message: Message):

    ads = AdsManager.active_channels()

    if not ads:
        return await message.answer(
            "📭 There are no active channel advertisements."
        )

    for ad in ads:

        ad_id = ad[0]
        owner_id = ad[1]
        link = ad[2]
        target = ad[3]
        current = ad[4]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{link.replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify",
                        callback_data=f"verify_channel_{ad_id}"
                    )
                ]
            ]
        )

        remain = target - current

        text = (
            "📢 <b>Channel Advertisement</b>\n\n"
            f"🔗 {link}\n\n"
            f"💰 Reward : {REWARD:.2f} Birr\n"
            f"👥 Progress : {current}/{target}\n"
            f"⌛ Remaining : {remain}"
        )

        await message.answer(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
@router.callback_query(F.data.startswith("verify_channel_"))
async def verify_channel(
    callback: CallbackQuery,
    bot: Bot
):

    ad_id = int(callback.data.split("_")[2])

    user_id = callback.from_user.id

    campaign = AdsManager.get_campaign(ad_id)

    if campaign is None:

        return await callback.answer(
            "❌ Advertisement not found.",
            show_alert=True
        )

    link = campaign["link"]

    try:

        member = await bot.get_chat_member(
            chat_id=link,
            user_id=user_id
        )

        if member.status in (
            "left",
            "kicked"
        ):

            return await callback.answer(
                "❌ You must join the channel first.",
                show_alert=True
            )

    except Exception:

        return await callback.answer(
            "❌ Unable to verify channel.",
            show_alert=True
        )

    result = AdsManager.complete_campaign(
        user_id=user_id,
        ad_id=ad_id
    )

    if not result["success"]:

        return await callback.answer(
            result["message"],
            show_alert=True
        )

    await callback.answer(
        f"🎉 +0.27 Birr added successfully.",
        show_alert=True
    )

    try:

        info = AdsManager.campaign_info(ad_id)

        remain = info["target"] - info["current"]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{info['link'].replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verified",
                        callback_data="verified"
                    )
                ]
            ]
        )

        await callback.message.edit_text(

            "📢 <b>Channel Advertisement</b>\n\n"

            f"🔗 {info['link']}\n\n"

            f"💰 Reward : 0.27 Birr\n"

            f"👥 Progress : {info['current']}/{info['target']}\n"

            f"⌛ Remaining : {remain}",

            parse_mode="HTML",
            reply_markup=keyboard

        )

    except Exception:
        pass
from db import get_balance


# ==========================
# CHANNEL INFORMATION
# ==========================

@router.callback_query(F.data.startswith("channel_info_"))
async def channel_info(
    callback: CallbackQuery
):

    ad_id = int(callback.data.split("_")[2])

    info = AdsManager.campaign_info(ad_id)

    if info is None:
        return await callback.answer(
            "Advertisement not found.",
            show_alert=True
        )

    progress = (
        info["current"] / info["target"]
    ) * 100

    remaining = info["target"] - info["current"]

    text = (
        "📊 <b>Advertisement Information</b>\n\n"
        f"🆔 ID : <code>{info['id']}</code>\n"
        f"📢 Type : {info['type'].title()}\n"
        f"🔗 Link : {info['link']}\n\n"
        f"👥 Progress : {info['current']}/{info['target']}\n"
        f"📈 Completed : {progress:.1f}%\n"
        f"⌛ Remaining : {remaining}\n"
        f"💰 Reward : 0.27 Birr\n"
        f"📌 Status : {info['status'].title()}"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML"
    )

    await callback.answer()


# ==========================
# USER BALANCE
# ==========================

@router.message(F.text == "💰 Balance")
async def my_balance(message: Message):

    balance = get_balance(message.from_user.id)

    text = (
        "💰 <b>Your Balance</b>\n\n"
        f"💳 Deposit : {balance['deposit']:.2f} Birr\n"
        f"💵 Earned : {balance['earned']:.2f} Birr"
    )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# ==========================
# REFRESH CHANNELS
# ==========================

@router.message(F.text == "🔄 Refresh Channels")
async def refresh_channels(message: Message):

    ads = AdsManager.active_channels()

    if not ads:
        return await message.answer(
            "📭 No active advertisements."
        )

    await join_channels(message)
from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from ads_manager import AdsManager

router = Router()

VERIFY_BOT = "YourVerifyBot"   # @YourVerifyBot


@router.message(F.text == "📢 Join Channels")
async def join_channels(message: Message):

    ads = AdsManager.active_channels()

    if not ads:
        return await message.answer(
            "📭 No active channel advertisements."
        )

    for ad in ads:

        ad_id = ad[0]
        link = ad[2]
        target = ad[3]
        current = ad[4]

        code = AdsManager.generate_code(
            message.from_user.id,
            ad_id
        )

        verify_url = (
            f"https://t.me/{VERIFY_BOT}"
            f"?start={code}"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Join Channel",
                        url=f"https://t.me/{link.replace('@','')}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Verify Join",
                        url=verify_url
                    )
                ]
            ]
        )

        remaining = target - current

        text = (
            "📢 <b>Channel Advertisement</b>\n\n"

            f"🔗 {link}\n\n"

            f"💰 Reward : <b>0.27 Birr</b>\n"

            f"👥 Progress : <b>{current}/{target}</b>\n"

            f"⌛ Remaining : <b>{remaining}</b>\n\n"

            "1️⃣ Join the channel.\n"
            "2️⃣ Click Verify Join.\n"
            "3️⃣ Verification Bot will reward you automatically."
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from ads_manager import AdsManager

verify_router = Router()


@verify_router.message(CommandStart())
async def verification_start(
    message: Message,
    state: FSMContext
):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:

        return await message.answer(
            "❌ Verification code not found."
        )

    code = args[1]

    result = AdsManager.verify(code)

    if result is None:

        return await message.answer(
            "❌ Invalid or expired verification code."
        )

    complete = AdsManager.complete_campaign(
        user_id=message.from_user.id,
        ad_id=result["ad_id"]
    )

    if not complete["success"]:

        return await message.answer(
            complete["message"]
        )

    info = AdsManager.campaign_info(
        result["ad_id"]
    )

    remaining = (
        info["target"] -
        info["current"]
    )

    await message.answer(

        "🎉 <b>Verification Successful</b>\n\n"

        "✅ Task Completed Successfully.\n\n"

        "💰 Reward Added : <b>0.27 Birr</b>\n"

        f"👥 Campaign Progress : {info['current']}/{info['target']}\n"

        f"⌛ Remaining : {remaining}",

        parse_mode="HTML"

    )

    if remaining <= 0:

        AdsManager.finish_campaign(
            result["ad_id"]
        )

        owner = info["owner"]

        try:

            await message.bot.send_message(

                owner,

                "🎉 Your advertisement has been completed.\n\n"

                f"👥 Target : {info['target']}\n"

                "✅ Campaign Closed Automatically."

            )

        except Exception:
            pass