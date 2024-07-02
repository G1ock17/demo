from aiogram.types import Message
from main import dp, bot
from database import functions


@dp.message_handler(text='Мой профиль')
async def my_profile(message: Message):
    data = functions.get_user_information(message.from_user.id)
    await message.answer(text='Ваш профиль:\n\n'
                              f'Ваш ID:<code> {data[0]}</code>\n'
                              f'Дата регестрации: {data[1][:16]}\n'
                              f'Ваш баланс: {data[2]}₽\n'
                              f'Ваши реквезиты: {data[3]}', parse_mode='html')