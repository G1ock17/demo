from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes
from main import dp, bot
from data import config
from database import functions
from aiogram.types import InlineKeyboardMarkup
from keyboards import keys


@dp.callback_query_handler(lambda c: c.data == 'get_gift')
async def support_request(callback: CallbackQuery):
    keyboard = keys.share_phone_markup()
    await bot.send_message(chat_id=callback.from_user.id, text=f'{callback.from_user.full_name}\n'
                                                               'У нас для тебя подарок за отзыв. \n\n'
                                                               'Пожалуйста, введи в ответном сообщении свой номер телефона, на него мы отправим бонус!\n'
                                                               'Или нажми на кнопку «Поделиться номером»', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'support_request')
async def support_request(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(keys.ikb('Качество товара', 'ask_quality_product'),
                 keys.ikb('Комплектация товара', 'ask_equipment_product'),
                 keys.ikb('Другой вопрос', 'ask_any_question'))

    await callback.message.answer(text='<b>Выбери пожалуйста категорию обращения: </b>', reply_markup=keyboard,
                                  parse_mode='html')
    await callback.answer()


class UsedAsk(StatesGroup):
    asked = State()


@dp.callback_query_handler(lambda c: c.data.startswith('ask_'))
async def quality_product(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        ask_type = callback.data.split('_', 1)[1]
        data['ask_type'] = ask_type

    await callback.message.answer(
        text=f'Пожалуйста подробно опиши проблему в ответном сообщении. Также приложите фотографии, демонстрирующие проблему.\n'
             f'Ответим в течение 24 ч.\n'
             f'После того как вы отправите свое обращение нажмите ✅ Подтвердить', reply_markup=keys.confirm_markup(),
        parse_mode='html')
    await UsedAsk.asked.set()
    await callback.answer()


@dp.message_handler(state=UsedAsk.asked)
async def enter_key2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text
    if message.text == '✅ Подтвердить':
        await state.finish()
        await message.answer(text=f'Готово!\nМы ответим в течение 24 ч.', reply_markup=keys.confirm_markup(),
                             parse_mode='html')
    else:
        if data['ask_type'] == 'quality_product':
            await bot.send_message(chat_id=config.GROUP_ID,
                                   text=f"{message.from_user.id}\nКачество товара\n{data['ask']}")
        if data['ask_type'] == 'equipment_product':
            await bot.send_message(chat_id=config.GROUP_ID,
                                   text=f"{message.from_user.id}\nКомплектация товара\n{data['ask']}")
        if data['ask_type'] == 'any_question':
            await bot.send_message(chat_id=config.GROUP_ID,
                                   text=f"{message.from_user.id}\nДругой вопрос\n{data['ask']}")

        await message.answer(text=f'Если вы написали все что хотели нажмите ✅ Подтвердить',
                             reply_markup=keys.confirm_markup(),
                             parse_mode='html')


@dp.message_handler(content_types=['photo'], state=UsedAsk.asked)
async def send_photo_to_group(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await bot.send_photo(chat_id=config.GROUP_ID, photo=photo.file_id, caption=f'{message.from_user.id}')
    # 3-4

    await message.answer("Фотография сохранена! Если вы загрузили все свои фотографии нажмите ✅ Подтвердить")


@dp.message_handler(content_types=ContentTypes.TEXT)
async def handle_text_message(message: Message):
    if message.reply_to_message:
        if message.chat.id == config.GROUP_ID:
            user_id = int(message.reply_to_message.text.split('\n')[0])
            await bot.send_message(chat_id=user_id, text=message.text)


@dp.callback_query_handler(lambda callback: callback.data.startswith(('confirm_', 'rewrite_')))
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    action, phone_number = callback.data.split('_')
    if action == "confirm":
        functions.add_phone(callback.from_user.id, phone_number)
        print(phone_number, callback.message.from_user.id)
        await bot.answer_callback_query(callback.id)
        await state.update_data(confirm=True)

        await bot.send_message(callback.from_user.id,
                               'Отлично! А теперь пришли пожалуйста, <b>скриншот</b> твоего отзыва о товаре. '
                               'Мы все проверим и пришлем подарок.\n\n'
                               'Если отзыв еще не оставлен, то можно это сделать прямо сейчас 😄', parse_mode='html')

    elif action == "rewrite":
        await callback.message.answer("Пожалуйста, введите свой номер телефона еще раз.")


@dp.callback_query_handler(lambda callback: callback.data in ['bonus_sent', 'reject'], state='*')
async def feedback_confirmation_callback(callback: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)

    data = await state.get_data()
    sub_status = functions.get_sub_status(callback.from_user.id)
    phone = functions.get_user_phone(callback.from_user.id)
    if callback.data == 'bonus_sent':
        if sub_status:  # здесь можно прописать логику подарков
            functions.switch_sub_status(callback.from_user.id)
            await bot.send_message(callback.from_user.id, '✅ Подарок отправлен\n'
                                                          f'Спасибо за отзыв! Мы все проверили и зачислили вам подарок на номер телефона {phone}')
            await bot.send_message(callback.from_user.id,
                                   f'{callback.from_user.full_name} если у вас остались вопросы, жмите на кнопку ниже\n- Написать продавцу')
        else:
            await bot.send_message(callback.from_user.id, '❌ Вы уже получали подарок\n'
                                                          'Получить ещё один к сожалению не получится')
    elif callback.data == 'reject':
        await bot.send_message(callback.from_user.id, '❌ Отзыв отклонен\n'
                                                      'Сожалеем, но что-то пошло не так. Пожалуйста, попробуйте еще раз.')

    # Сбрасываем состояние
    await state.finish()
