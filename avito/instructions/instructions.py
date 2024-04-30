from aiogram.types import Message, InputMediaPhoto, InputFile, MediaGroup
from main import dp, bot
from database import functions
import os


@dp.message_handler(text='Инструкция')
async def send_instruction1(message: Message):
    caption_text = 'ТОЙОТА КАМРИ, 2016\nVIN: XW7BF4FK80S130385\nГосномер: К450КО\nНомер кузова: XW7B*************\nНомер шасси:\nТип кузова: Легковой седан\nЦвет: Черный\nМощность двигателя: 181.0 л. с.\nОбъём двигателя: 2494 куб. см\nМасса без нагрузки: 1570 кг\nРазрешенная максимальная масса: 2100 кг\nГод выпуска: 2016\nКатегория: B\nРасположение руля: Левостороннее\nТип двигателя: Бензиновый\nТип привода: Передний\nТип трансмиссии: Автоматическая\n\nПТС оригинал\nВладелец 1\n\nПробег 107 933\nМесто встречи Москва метро Аннино\n\nНе битый'
    text2 = ('КАК ОПРЕДЕЛЯЕМ ПРОБЕГ 💥\n'
             'Пробег:\n'
             'Год от  2011-2013  *160-170 тысяч \n'
             'Год от 2014-2017  *130-150 тысяч \n'
             'Год от 2017 - 2020 * 80-120 тысяч\n\n'

             'ПТС оригинал - всегда\n'
             'Владелец от 1-3 (делаем на свое усмотрение и считая по году)\n\n'

             'Не битый (всегда)\n'
             'Место встречи Москва и любое метро (не центральное)\n\n'

             'Цена:\n\n'

             'До 1500 000 - вычитаем 100 к\n'
             'От 1600 - 1800 - вычитаем 150 к\n'
             'От 1900 - 2200 - вычитаем 200-260 к\n\n'

             'Смотрим всегда только на минимальную стоимость от оценки Авито, от нее и отнимаем')


    media = MediaGroup()
    media.attach_photo(InputFile('instructions/1/1.jpg'))
    media.attach_photo(InputFile('instructions/1/2.jpg'))
    media.attach_photo(InputFile('instructions/1/3.jpg'))
    media.attach_photo(InputFile('instructions/1/4.jpg'))
    media.attach_photo(InputFile('instructions/1/5.jpg'))
    media.attach_photo(InputFile('instructions/1/6.jpg'))
    media.attach_photo(InputFile('instructions/1/7.jpg'))
    media.attach_photo(InputFile('instructions/1/8.jpg'))


    media2 = MediaGroup()
    media2.attach_photo(InputFile('instructions/2/1.jpg'))
    media2.attach_photo(InputFile('instructions/2/2.jpg'))
    media2.attach_photo(InputFile('instructions/2/3.jpg'))
    media2.attach_photo(InputFile('instructions/2/4.jpg'))
    media2.attach_photo(InputFile('instructions/2/5.jpg'))

    await message.answer(text=caption_text)
    await message.reply_media_group(media=media)
    await message.answer(text=text2)
    await message.reply_media_group(media=media2)

