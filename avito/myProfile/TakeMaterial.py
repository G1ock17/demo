from aiogram.types import Message, ContentTypes
from main import dp, bot
from database import functions


@dp.message_handler(text='Взять материал')
async def get_request(message: Message):
    max_limit = functions.get_user_limit_value(message.from_user.id)
    user_req_value = functions.get_user_requests_value(message.from_user.id)

    if max_limit > user_req_value:

        functions.add_request(message.from_user.id)
        await bot.send_message(chat_id=message.chat.id, text='Заявка на получение материала отправленна модераторам.'
                                                             '\nПосле одобрения заявки, вам придет уведомление.'
                                                             f'\nВам доступно еще {max_limit-user_req_value-1} материала')
    else:
        await bot.send_message(chat_id=message.chat.id, text='Вы уже отправляли завявку на получение материала.'
                                                             '\nДождитесь одобрения модерацией')