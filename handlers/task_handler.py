from ads_manager import update_ad_progress

# ተጠቃሚው 'Verify' የሚለውን በተን ሲጫን የሚሰራው
async def verify_handler(message: Message, state: FSMContext):
    # ad_id ን ከ state ወይም ከ callback_data ታገኛለህ
    is_completed = await update_ad_progress(ad_id)
    
    if is_completed:
        await message.answer("🎉 እንኳን ደስ አለዎት! ማስታወቂያው ዒላማው ላይ ደርሶ ተዘግቷል።")
    else:
        await message.answer("✅ ስራዎ ተረጋግጧል!")