from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ContentTypes
from main import dp, bot
from data import config
from keyboards import keys
from database import functions


class ChangeRequisite(StatesGroup):
    request = State()


@dp.message_handler(text='Изменить реквезиты')
async def change_req(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.from_user.id
    await ChangeRequisite.request.set()
    await bot.send_message(chat_id=message.chat.id, text='<b>Введите ваши новые реквезиты.</b>(16 цифр банковской карты)',
                           reply_markup=keys.cancel(),
                           parse_mode='html')


@dp.message_handler(state=ChangeRequisite.request, content_types=ContentTypes.TEXT)
async def enter_key(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['request'] = message.text
        if data['request'].isdigit() and len(data['request']) == 16:
            user_id = data['user_id']
            functions.change_requisite(user_id, data['request'])
            await message.answer(text='Ваши реквизиты успешно обновленны', reply_markup=keys.main_markup())
            await state.finish()
        else:
            await message.answer(text='Введите корректные реквезиты вашей карты.\nНапример 1234432112344321')