from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from main import dp, bot
from data import config
from database import functions
from keyboards import keys
from filters import IsUser
from filters import IsAdmin


@dp.message_handler(Command('start'))
async def start(message: Message):
    if functions.check_new_user(message.from_user.id):
        functions.add_user(message.from_user.id)
    else:
        pass

    keyboard = InlineKeyboardMarkup()
    keyboard.add(keys.ikb('Получить подарок', 'get_gift'), keys.ikb('Написать продавцу', 'support_request'))
    await bot.send_message(chat_id=message.chat.id,
                           text='Привет! Благодарим тебя за покупку!'
                                '\nНадеемся, что тебе или твоим близким понравится наш товар.  В качестве благодарности за доверие, мы хотим тебе сделать подарок 🎁',
                           reply_markup=keyboard, parse_mode='html')


@dp.message_handler(text='Написать продавцу')
async def support_request2(message: Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(keys.ikb('Качество товара', 'ask_quality_product'),
                 keys.ikb('Комплектация товара', 'ask_equipment_product'),
                 keys.ikb('Другой вопрос', 'ask_any_question'))
    await message.answer(text='<b>Выбери пожалуйста категорию обращения: </b>', reply_markup=keyboard, parse_mode='html')


@dp.message_handler(text='Получить подарок')
async def get_gift(message: Message):
    keyboard = keys.share_phone_markup()
    await bot.send_message(chat_id=message.from_user.id, text=f'{message.from_user.full_name}\n'
                                'У нас для тебя подарок за отзыв. \n\n'
                                'Пожалуйста, введи в ответном сообщении свой номер телефона, на него мы отправим бонус!\n'
                                'Или нажми на кнопку «Поделиться номером»', reply_markup=keyboard)


@dp.message_handler(Command('close'))
async def handle_message(message: Message):
    if message.from_user.id in config.ADMINS:
        command, *args = message.get_full_command()

        if args:
            try:
                user_id = int(args[0])
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(KeyboardButton('Поделиться номером', request_contact=True))
                await bot.send_message(chat_id=user_id,
                                       text=f'{message.from_user.full_name}, рады, что удалось решить ваш вопрос!\n'
                                            'У нас для тебя подарок за отзыв. \n\n'
                                            'Пожалуйста, введи в ответном сообщении свой номер телефона, на него мы отправим бонус!\n'
                                            'Или нажми на кнопку «Поделиться номером»',
                                       reply_markup=keyboard)
            except ValueError:
                await message.answer("ID пользователя должен быть числом.")
        else:
            await message.answer("Пожалуйста, введите ID пользователя после команды.")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")


@dp.message_handler(content_types=ContentTypes.CONTACT)
async def handle_contact(message: Message):
    phone_number = message.contact.phone_number
    print(phone_number)
    await message.answer(f"Ты поделился номером: {phone_number}\n\n"
                         "Пожалуйста, подтверди, что номер верный:",
                         reply_markup=keys.get_confirmation_keyboard(phone_number))


@dp.message_handler(content_types=ContentTypes.PHOTO, state='*')
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    confirm = data.get('confirm', False)
    if not confirm:
        await message.answer("Сначала подтвердите отправку отзыва кнопкой 'Поделиться отзывом'.")
        return
    await message.answer(f"💬Супер, спасибо!"
                         "Скоро мы все проверим. Ответ поступит в этот бот - не останавливайте его.")
    await state.update_data(screenshot=message.photo[-1])
    photo = message.photo[-1]
    phone = functions.get_user_phone(message.from_user.id)
    await bot.send_photo(chat_id=config.GROUP_ID, photo=photo.file_id, caption=f'{message.from_user.id}')
    await bot.send_message(chat_id=config.GROUP_ID,
                           text=f'Нужно проверить этот отзыв и начислить деньги на номер {phone}\n\n',
                           reply_markup=keys.get_feedback_confirmation_keyboard())
