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
    keyboard = ikb_user('out_money')
    if keyboard:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.answer(text=f'У вас нет материала')


@dp.callback_query_handler(lambda c: c.data.startswith('req_'))
async def process_product_selection(callback_query: CallbackQuery):
    req_type = callback_query.data.split('_')[1]
    type_id = callback_query.data.split('_')[2]
    print(type_id)
    if req_type == 'material':
        pass
    elif req_type == 'anc':
        pass
    elif req_type == 'payment':
        try:
            description = functions.get_application(type_id)

            for request in description:
                request_id = request[0]
                requisite = request[1]
                value = request[3]
                date = request[4]
                status = request[5]
                status_text = "На проверке" if status == 0 else status

                await callback_query.message.answer(
                    text=f'Заявка №{request_id}\n\n'
                         f'Сумма: <b>{value}</b>р\n'
                         f'Реквизиты: <b>{requisite}</b>\n'
                         f'Дата: <b>{date[:16]}</b>\n'
                         f'Статус: <b>{status_text}</b>\n',
                    parse_mode='html'
                )
        except Exception as e:
            print(f"Произошла ошибка при обработке заявки: {e}")