from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📢 Join Channels"),
            KeyboardButton(text="🤖 Join Bots")
        ],
        [
            KeyboardButton(text="💰 Balance"),
            KeyboardButton(text="💸 Withdraw")
        ],
        [
            KeyboardButton(text="📣 Advertise"),
            KeyboardButton(text="👥 Referrals")
        ],
        [
            KeyboardButton(text="ℹ️ Info")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Select an option..."
)