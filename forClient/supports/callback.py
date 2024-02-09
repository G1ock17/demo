from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes, InputMediaPhoto
from main import dp, bot
from data import config
from database import functions
from aiogram.types import InlineKeyboardMarkup
from keyboards import keys

from supports.menu import GiftState, Review


class UsedAsk(StatesGroup):
    asked = State()


@dp.callback_query_handler(lambda c: c.data == 'get_gift')
async def support_request(callback: CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id, text=f'{callback.from_user.full_name}\n'
                                                               'У нас для тебя подарок за отзыв. \n\n'
                                                               'Пожалуйста, введи в ответном сообщении свой номер телефона, на него мы отправим бонус!\n'
                                                               'Или нажми на кнопку «Поделиться номером»',
                           reply_markup=keys.share_phone_markup())
    await GiftState.WaitingForPhoneNumber.set()


@dp.callback_query_handler(lambda c: c.data == 'support_request')
async def support_request(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(keys.ikb('Качество товара', 'ask_quality_product'),
                 keys.ikb('Комплектация товара', 'ask_equipment_product'),
                 keys.ikb('Другой вопрос', 'ask_any_question'))

    await callback.message.answer(text='<b>Выбери пожалуйста категорию обращения: </b>', reply_markup=keyboard,
                                  parse_mode='html')
    await callback.answer()


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


@dp.message_handler(content_types=ContentTypes.TEXT, state=UsedAsk.asked)
async def enter_key1(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text

    if message.text == '✅ Подтвердить':
        functions.add_log('requests')
        await state.finish()
        await message.answer(text=f'Готово!\nМы ответим в течение 24 ч.', reply_markup=keys.main_markup(),
                             parse_mode='html')
        return

    type_ask = None

    if data['ask_type'] == 'quality_product':
        type_ask = 'Качество товара'
    elif data['ask_type'] == 'equipment_product':
        type_ask = 'Комплектация товара'
    elif data['ask_type'] == 'any_question':
        type_ask = 'Другой вопрос'

    await bot.send_message(chat_id=config.GROUP_ID,
                           text=f"{message.from_user.id}\n{type_ask}\n{data['ask']}")

    await message.answer("Сообщение отправлено! Если вы отправили все хотели, нажмите ✅ Подтвердить")


@dp.message_handler(content_types=ContentTypes.PHOTO, state=UsedAsk.asked)
async def enter_key2(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['ask'] = message.text
    type_ask = None
    if data['ask_type'] == 'quality_product':
        type_ask = 'Качество товара'
    elif data['ask_type'] == 'equipment_product':
        type_ask = 'Комплектация товара'
    elif data['ask_type'] == 'any_question':
        type_ask = 'Другой вопрос'

    await state.update_data(screenshot=message.photo[-1])
    photo = message.photo[-1]
    await bot.send_photo(chat_id=config.GROUP_ID, photo=photo.file_id, caption=f'{message.from_user.id}\n{type_ask}')
    await message.answer('Ваш скриншот успешно отправлен на модерацию ✅')


@dp.message_handler(content_types=ContentTypes.ANY)
async def handle_text_message(message: Message):
    if message.reply_to_message:
        if message.chat.id == config.GROUP_ID:
            user_id = int(message.reply_to_message.text.split('\n')[0])
            await bot.send_message(chat_id=user_id, text=message.text)
            functions.add_log('answers')
            functions.add_answer_logs(message.from_user.username, message.text)
            await bot.send_message(chat_id=config.GROUP_ID, text='Ваш ответ доставленн пользователю')
            hesoyam = functions.get_answers_logs()
            print(functions.get_answers_logs())


@dp.callback_query_handler(lambda callback: callback.data.startswith(('confirm_', 'rewrite_')), state=GiftState.WaitingForPhoneNumber)
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    action, phone_number = callback.data.split('_')
    if action == "confirm":
        functions.add_phone(callback.from_user.id, phone_number)

        await bot.answer_callback_query(callback.id)
        await Review.WaitingForReview.set()
        await bot.send_message(chat_id=callback.from_user.id, text=
                               'Отлично! А теперь пришли пожалуйста, <b>скриншот</b> твоего отзыва о товаре. '
                               'Мы все проверим и пришлем подарок.\n\n'
                               'Если отзыв еще не оставлен, то можно это сделать прямо сейчас 😄', reply_markup=keys.main_markup(), parse_mode='html')

    elif action == "rewrite":
        await GiftState.WaitingForPhoneNumber.set()
        await callback.message.answer("Пожалуйста, введите свой номер телефона еще раз.")


@dp.callback_query_handler(lambda callback: callback.data in ['bonus_sent', 'reject'])
async def feedback_confirmation_callback(callback: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    sub_status = functions.get_sub_status(callback.from_user.id)
    phone = functions.get_user_phone(callback.from_user.id)
    if callback.data == 'bonus_sent':
        if sub_status:  # здесь можно прописать логику подарков
            functions.switch_sub_status(callback.from_user.id)
            await bot.send_message(callback.from_user.id, '✅ Подарок отправлен\n'
                                                          f'Спасибо за отзыв! Мы все проверили и зачислили вам подарок на номер телефона {phone}')
            await bot.send_message(chat_id=callback.from_user.id,
                                   text=f'{callback.from_user.full_name} если у вас остались вопросы, жмите на кнопку ниже\n- Написать продавцу',
                                   reply_markup=keys.main_markup(), parse_mode='html')
        else:
            await bot.send_message(callback.from_user.id, '❌ Вы уже получали подарок\n'
                                                          'Получить ещё один к сожалению не получится')
    elif callback.data == 'reject':
        await bot.send_message(chat_id=callback.from_user.id,
                               text='❌ Отзыв отклонен\nСожалеем, но что-то пошло не так. Пожалуйста, попробуйте еще раз.',
                               reply_markup=keys.main_markup(), parse_mode='html')
    await state.finish()
