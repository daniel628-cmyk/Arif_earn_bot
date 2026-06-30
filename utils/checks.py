# utils/checks.py
async def check_user_sub(bot, chat_id, user_id):
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        # ተጠቃሚው ቻናሉ ውስጥ መሆኑን ያረጋግጣል
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False