from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📢 Join Channels"),
            KeyboardButton(text="🤖 Join Bots"),
            KeyboardButton(text="📺 Watch Ads"),
        ],
        [
            KeyboardButton(text="📤 Withdraw"),
            KeyboardButton(text="💰 Balance"),
            KeyboardButton(text="ℹ️ Info"),
        ],
        [
            KeyboardButton(text="👫 Referrals"),
            KeyboardButton(text="📊 Advertise"),
        ],
    ],
    resize_keyboard=True,
    is_persistent=True
)