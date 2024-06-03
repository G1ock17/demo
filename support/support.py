from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ContentTypes
from main import dp, bot
from data import config
from keyboards import keys


class UsedAsk(StatesGroup):
    asked = State()


@dp.message_handler(text='Написать в поддержку')
async def send_to_sup_chat(message: Message):
    await UsedAsk.asked.set()
    await bot.send_message(chat_id=message.chat.id, text='<b>Задайте вопрос свой вопрос.</b>',
                           reply_markup=keys.cancel(),
                           parse_mode='html')


@dp.message_handler(state=UsedAsk.asked)
async def enter_key(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text
        await bot.send_message(chat_id=config.GROUP_ID, text=f"{message.from_user.id}\n{data['ask']}")
        await message.answer(text='Ваш вопрос отправлен модераторам.', reply_markup=keys.main_markup())
        await state.finish()


@dp.message_handler(content_types=ContentTypes.TEXT)
async def handle_text_message(message: Message):
    if message.reply_to_message:
        if message.chat.id == config.GROUP_ID:
            user_id = int(message.reply_to_message.text.split('\n')[0])
            await bot.send_message(chat_id=user_id, text=message.text)