# አሮጌው መስመር፡ @router.message(F.text == "📢 Advertise")
# በአዲሱ ይህንን ተካው፡
@router.message(F.text == "📣 Advertise")
async def start_advertise(message: Message, state: FSMContext):
    await message.answer("📢 ለማስተዋወቅ የሚፈልጉትን የቻናል ሊንክ (ለምሳሌ: https://t.me/username) ይላኩ።")
    await state.set_state(AdvertiseState.waiting_for_link)