from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, ContentTypes, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from main import dp, bot
from aiogram.dispatcher.filters import Command
from data import config
from database import functions
from keyboards import keys


def ikb_user(table):
    keyboard = InlineKeyboardMarkup(row_width=1)
    names = functions.admin_get_req(table)
    if names:
        materials = [name[0] for name in names]
        for material in materials:
            button = InlineKeyboardButton(material, callback_data=f"adm_{table}_{material}")
            keyboard.add(button)
        button = InlineKeyboardButton('Назад', callback_data=f"back_to_admin_menu")
        keyboard.add(button)
        return keyboard
    else:
        return None


@dp.message_handler(Command('admin'), state='*')
async def admin(message: Message, state: FSMContext):
    await state.finish()
    if message.from_user.id in config.ADMINS:
        await bot.send_message(chat_id=message.chat.id,
                               text='Выберите отдел:', reply_markup=keys.admin_menu(), parse_mode='html')
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Вы не админ', reply_markup=keys.main_markup())


@dp.callback_query_handler(lambda c: c.data == 'back_to_admin_menu')
async def support_request(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=keys.admin_menu())


@dp.callback_query_handler(lambda c: c.data == 'req_material')
async def support_request(callback: CallbackQuery):
    keyboard = ikb_user('requests')
    if keyboard:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.answer(text=f'У вас нет материала')


@dp.callback_query_handler(lambda c: c.data == 'req_anc')
async def support_request(callback: CallbackQuery):
    keyboard = ikb_user('anc')
    if keyboard:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.answer(text=f'У вас нет материала')


@dp.callback_query_handler(lambda c: c.data == 'req_payment')
async def support_request(callback: CallbackQuery):
    keyboard = ikb_user('money')
    if keyboard:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.answer(text=f'У вас нет материала')


@dp.callback_query_handler(lambda c: c.data.startswith('adm_'))
async def process_product_selection(callback: CallbackQuery):
    req_type = callback.data.split('_')[1]
    type_id = callback.data.split('_')[2]

    if req_type == 'requests':
        try:
            description = functions.admin_get_info_req(req_type, type_id)

            for request in description:
                request_id = request[0]
                user_id = request[1]
                date = request[2]
                status = request[3]

                keyboard = InlineKeyboardMarkup()
                keyboard.add(keys.ikb('👍', f'accept_{req_type}_{request_id}'),
                             keys.ikb('👎', f'cancel_{req_type}_{request_id}'))

                await callback.message.answer(
                    text=f'Заявка №{request_id}\n\n'
                         f'User: <b>{user_id}</b>\n'
                         f'Дата: <b>{date[:16]}</b>\n', reply_markup=keyboard,
                    parse_mode='html'
                )
        except Exception as e:
            print(f"Произошла ошибка при обработке заявки: {e}")

    if req_type == 'anc':
        try:
            description = functions.admin_get_info_req(req_type, type_id)

            for request in description:
                request_id = request[0]
                user_id = request[1]
                date = request[2]
                link = request[3]
                status = request[4]

                keyboard = InlineKeyboardMarkup()
                keyboard.add(keys.ikb('👍', f'accept_{req_type}_{request_id}'),
                             keys.ikb('👎', f'cancel_{req_type}_{request_id}'))

                await callback.message.answer(
                    text=f'Заявка на проврку объявления №{request_id}\n\n'
                         f'User: <b>{user_id}</b>\n'
                         f'Дата: <b>{date[:16]}</b>\n'
                         f'Ссылка на объявление: <b>{link}</b>\n', reply_markup=keyboard,
                    parse_mode='html'
                )

        except Exception as e:
            print(f"Произошла ошибка при обработке заявки: {e}")

    if req_type == 'money':
        try:
            description = functions.admin_get_info_req(req_type, type_id)
            for request in description:
                request_id = request[0]
                requisite = request[1]
                value = request[3]
                date = request[4]
                status = request[5]

                keyboard = InlineKeyboardMarkup()
                keyboard.add(keys.ikb('👍', f'accept_{req_type}_{request_id}'),
                             keys.ikb('👎', f'cancel_{req_type}_{request_id}'))

                await callback.message.answer(
                    text=f'Заявка №{request_id}\n\n'
                         f'Сумма: <b>{value}</b>р\n'
                         f'Реквизиты: <b>{requisite}</b>\n'
                         f'Дата: <b>{date[:16]}</b>\n', reply_markup=keyboard,
                    parse_mode='html'
                )

        except Exception as e:
            print(f"Произошла ошибка при обработке заявки: {e}")


@dp.callback_query_handler(lambda callback: callback.data.startswith(('accept_', 'cancel_')))
async def handle_confirmation(callback: CallbackQuery):
    action, req_type, type_id = callback.data.split('_')
    user_id = callback.from_user.id

    if action == "accept":

        if req_type == 'anc':
            functions.update_status_and_get_user_id(req_type, type_id, 2)
            text = 'Ваше объявление одобренно, на ваш счет зачисленно <b>300р</b>.'
            functions.update_user_balance(user_id, 300, '+')
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')
        if req_type == 'money':
            # функция для снятия денег со счета
            functions.update_status_and_get_user_id(req_type, type_id, 2)
            text = 'Ваша заявка на вывод средств одобренна.'
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')
        if req_type == 'requests':
        # функция для добавления материала для пользователя
            phone = functions.give_phone_for_user(int(callback.from_user.id))
            functions.update_status_phone_and_get_user_id(1, phone, callback.from_user.id, req_type, type_id)
            text = 'Ваша заявка на получение материала одобренна, вы можете посмотреть свой материал в разделе <b>Мой материал</b>'
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')
        else:
            await callback.message.answer('Нет свободного материалал.')


    if action == "cancel":
        if req_type == 'anc':
            functions.refusal_of_request(req_type, type_id)
            text = 'Ваше объявление не прошло проверку.'
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')
        if req_type == 'money':
            functions.refusal_of_request(req_type, type_id)
            text = 'Ваша заявка на вывод средств отклоненна.'
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')
        if req_type == 'requests':
            functions.refusal_of_request(req_type, type_id)
            text = 'Ваша заявка на получение материала отклонена.'
            await bot.delete_message(callback.message.chat.id, callback.message.message_id)
            await bot.send_message(user_id, text, reply_markup=keys.main_markup(), parse_mode='html')