from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[

        [
            InlineKeyboardButton(
                text="📢 Join Channels",
                callback_data="join_channels"
            )
        ],

        [
            InlineKeyboardButton(
                text="🤖 Join Bots",
                callback_data="join_bots"
            )
        ],

        [
            InlineKeyboardButton(
                text="💰 Balance",
                callback_data="balance"
            ),
            InlineKeyboardButton(
                text="💸 Withdraw",
                callback_data="withdraw"
            )
        ],

        [
            InlineKeyboardButton(
                text="👥 Referrals",
                callback_data="referrals"
            ),
            InlineKeyboardButton(
                text="📢 Advertising",
                callback_data="advertise"
            )
        ],

        [
            InlineKeyboardButton(
                text="ℹ️ Info",
                callback_data="info"
            )
        ]

    ]
)