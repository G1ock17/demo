from aiogram.types import Message
from main import dp, bot
from database import functions


@dp.message_handler(text='Мои заявки')
async def my_profile(message: Message):
    applications = functions.get_user_applications(message.from_user.id)
    await message.answer(text=f'Ваши заявки:', parse_mode='html')
    for request in applications:
        request_id = request[0]
        requisite = request[1]
        value = request[3]
        date = request[4]
        status = request[5]
        status_text = "На проверке" if status == 0 else status
        await message.answer(text=f'Заявка №{request_id}\n\n'
                                  f'Сумма: <b>{value}</b>\n'
                                  f'Реквезиты: <b>{requisite}</b>\n'
                                  f'Дата: <b>{date[:16]}</b>\n'
                                  f'Статус: <b>{status_text}</b>\n', parse_mode='html')
