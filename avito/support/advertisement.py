from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ContentTypes
from main import dp, bot
from data import config
from keyboards import keys


class CheckRequests(StatesGroup):
    request = State()


@dp.message_handler(text='Проверить объявление')
async def check(message: Message):
    await CheckRequests.request.set()
    await bot.send_message(chat_id=message.chat.id, text='<b>Введите ссылку на ваше объявление.</b>',
                           reply_markup=keys.cancel(),
                           parse_mode='html')


@dp.message_handler(state=CheckRequests.request)
async def enter_key(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text
        await bot.send_message(chat_id=config.GROUP_ID, text=f"{message.from_user.id}\n{data['ask']}")
        await message.answer(text='Ваш заявка отправлена на проверку.', reply_markup=keys.main_markup())
        await state.finish()


@dp.message_handler(content_types=ContentTypes.TEXT)
async def handle_text_message(message: Message):
    if message.reply_to_message:
        if message.chat.id == config.GROUP_ID:
            user_id = int(message.reply_to_message.text.split('\n')[0])
            await bot.send_message(chat_id=user_id, text=message.text)
