@dp.message_handler(text='Задать вопрос ?')
async def aboutus(message: Message):
    await UsedAsk.asked.set()
    await bot.send_message(chat_id=message.chat.id, text='<b>Задайте вопрос свой вопрос.</b>',
                           reply_markup=None,
                           parse_mode='html')


@dp.message_handler(state=UsedAsk.asked)
async def enter_key(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text
        await bot.send_message(chat_id=group_id, text=f"{message.from_user.id}\n{data['ask']}")
        await state.finish()


@dp.message_handler(content_types=ContentTypes.TEXT)
async def handle_text_message(message: Message):
    if message.reply_to_message:
        if message.chat.id == group_id:
            user_id = int(message.reply_to_message.text.split('\n')[0])
            await bot.send_message(chat_id=user_id, text=message.text)
