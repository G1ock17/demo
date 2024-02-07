from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ChatActions, LabeledPrice, ContentTypes
from main import dp, bot
from pyzbar.pyzbar import decode
import os
import keys as kb
from PIL import Image

async def decode_qr(message: Message):
    chat_id = message.chat.id

    if message.photo:
        photo = message.photo[-1]
    else:
        return

    file_info = await bot.get_file(photo.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open('qrcode.png', 'wb') as new_file:
        new_file.write(downloaded_file.read())

    try:
        result = decode(Image.open('qrcode.png'))
        await message.answer(result[0].data.decode("utf-8"))
        os.remove("qrcode.png")
    except Exception as e:
        await message.answer(str(e))


@dp.message_handler(content_types=ContentTypes.PHOTO)
async def handle_photos(message: Message):
    await decode_qr(message)
