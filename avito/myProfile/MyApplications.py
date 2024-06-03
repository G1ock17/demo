from aiogram.types import Message
from main import dp, bot
from database import functions
from aiogram.types import Message, CallbackQuery, ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton


def ikb_user_applications(user_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    names = functions.get_user_applications(user_id)
    applications = [name[0] for name in names]
    for application in applications:
        button = InlineKeyboardButton(application, callback_data=f"application_{application}")
        keyboard.add(button)
    return keyboard


@dp.message_handler(text='Мои заявки')
async def my_profile(message: Message):
    keyboard = ikb_user_applications(message.from_user.id)
    await message.answer(text=f'Ваши заявки:', parse_mode='html', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data.startswith('application_'))
async def process_product_selection(callback_query: CallbackQuery):
    application_id = callback_query.data.split('_')[1]

    try:
        description = functions.get_application(application_id)

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
