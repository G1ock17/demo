from aiogram.types import Message, ContentTypes
from main import dp, bot
from database import functions


@dp.message_handler(text='Взять материал')
async def get_request(message: Message):
    if functions.get_user_requests_status(message.from_user.id):
        functions.add_request(message.from_user.id)
        await bot.send_message(chat_id=message.chat.id, text='Заявка на получение материала отправленна модераторам.'
                                                             '\nПосле одобрения заявки, вам придет уведомление.')
    else:
        await bot.send_message(chat_id=message.chat.id, text='Вы уже отправляли завявку на получение материала.'
                                                             '\nДождитесь одобрения модерацией')