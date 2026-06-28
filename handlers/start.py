from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import get_db
from keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO users(user_id, username)
        VALUES(%s, %s)
        ON CONFLICT (user_id) DO NOTHING
        """,
        (
            message.from_user.id,
            message.from_user.username,
        ),
    )

    conn.commit()
    cur.close()

    await message.answer(
        "👋ሠላም እንኳን ወደ Arif earn Botመጣችሁ ",
        reply_markup=main_menu()
    )