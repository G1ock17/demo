from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ContentTypes
from main import dp, bot
from data import config
from keyboards import keys
from database import functions
import re


def check_avito_link(text):
    avito_pattern = r'https?://(www\.)?avito\.ru/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/[a-zA-Z0-9._-]+'
    links = re.findall(avito_pattern, text)

    if links:
        return True
    else:
        return None


class CheckRequests(StatesGroup):
    request = State()


@dp.message_handler(text='Проверить объявление')
async def check(message: Message):
    await CheckRequests.request.set()
    await bot.send_message(chat_id=message.chat.id, text='<b>Введите ссылку на ваше объявление.</b>',
                           reply_markup=keys.cancel(),
                           parse_mode='html')


# @dp.message_handler(state=CheckRequests.request)
# async def enter_key(message: Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['ask'] = message.text
#         await bot.send_message(chat_id=config.GROUP_ID, text=f"{message.from_user.id}\n{data['ask']}")
#         await message.answer(text='Ваш заявка отправлена на проверку.', reply_markup=keys.main_markup())
#         await state.finish()


@dp.message_handler(state=CheckRequests.request, content_types=ContentTypes.TEXT)
async def handle_text_message(message: Message):
    if check_avito_link(message.text):
        functions.add_link_if_not_exists(message.from_user.id, message.text)
        await bot.send_message(chat_id=message.from_user.id, text=f"Ваше объявление отправленно на проверку.\n{message.text}\n"
                                                                      f"После одобрения модерацией вы получите средства на счет.\n"
                                                                      f"Проверка объявление происходит в течении суток.",reply_markup=keys.main_markup())
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Введите корректную ссылку !")