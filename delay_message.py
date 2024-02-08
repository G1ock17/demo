from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from main import dp, bot
import asyncio


starttext = '<b>Ты хочешь продавать свои услуги в кайф, но у тебя:</b>\n\n'
perv1 = f'{starttext}👉Нет рабочего способа получать заявки:\n'
perv2 = f'{perv1}👉Не получается находить целевых людей\n'
perv3 = f'{perv2}👉 Не конвертят офферы или очень слабо\n\n'
perv4 = f'{perv3}<u>Значит ты в нужном месте 😎\n\n</u>'
perv5 = f'{perv4}<b>Я помогу собрать систему, которая приводит экспертам платежеспособную аудиторию через холодный трафик.</b>\n\n'
perv6 = f'{perv5}<i>⚠️ Эта система подойдет тем, у кого нет большой аудитории, технических навыков и команды</i>\n\n'

raketa1 = f'{perv6}🟥🟥🟥'
raketa2 = f'{perv6}🟨🟥🟥'
raketa3 = f'{perv6}🟨🟨🟥'
raketa4 = f'{perv6}🟩🟩🟩'
raketa5 = f'{perv6}🚀'
raketa6 = f'{raketa5}<b> Начинаем</b>'


@dp.message_handler(Command('start'))
async def start(message: Message):
    data_to_display = [starttext, perv1, perv2, perv4, perv5, perv6,
                       raketa1, raketa2, raketa3, raketa4, raketa5, raketa6]
    await send_message_with_delay(chat_id=message.chat.id, message_parts=data_to_display)

    
async def send_message_with_delay(chat_id, message_parts, delay=1):
    message = None
    for part in message_parts:
        if message:
            # Если уже есть сообщение, редактируем его
            await bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=part, parse_mode="html")
        else:
            # Если нет сообщения, отправляем новое
            message = await bot.send_message(chat_id=chat_id, text=part, parse_mode="html")
        await asyncio.sleep(delay)
