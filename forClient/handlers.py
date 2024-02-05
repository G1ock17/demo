from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
from main import dp, bot
import asyncio, sqlite3, re, func
import keys as kb
from data import config


@dp.message_handler(Command('menu'))
async def menu_message(message: Message):
    if message.from_user.id == ADMINS:
        await message.answer(text='<b>Welcome BOSS!</b>', reply_markup=kb.main_admin, parse_mode='html')
    else:
        await message.answer(text='Добро пожаловать!</b>', reply_markup=kb.main, parse_mode='html')


@dp.message_handler(Command('regist'))
async def start(message: Message):
    connect = sqlite3.connect('db.db')
    cursor = connect.cursor()
    cursor.execute("""SELECT user_id FROM info WHERE user_id=?""", [message.chat.id])
    user = cursor.fetchone()
    connect.commit()
    if not user:
        cursor.execute("""INSERT INTO info(user_tgname, user_id, sub_status, date) VALUES(?, ?, ?, ?)""",
                       [message.chat.first_name, message.chat.id, 0, date])
        connect.commit()
        cursor.close()
        connect.close()
        await AwaitMessages.fio_add.set()
        await bot.send_message(chat_id=message.chat.id, text='Ведите ваше имя:', reply_markup=kb.main)
    else:
        await bot.send_message(chat_id=message.chat.id, text='Вы уже зарегистрированы!', reply_markup=kb.main)


@dp.message_handler(text='О нас  📖')
async def aboutus(message: Message):
    if (func.is_registered(message.chat.id)):
        await bot.send_message(chat_id=message.chat.id,
                               text='⭐️ <b>Что такое GlockGPTChat</b> ⭐️'
                                    '\n\n📃 <b>GlockGPTChat</b> - это бот в Telegram, который помогает пользователям получать ответы на свои вопросы, используя мощную технологию генерации текста от <b>OpenAI.</b>'
                                    '\nБот был создан для того, чтобы сделать поиск и получение информации более удобным и быстрым.'
                                    '\n\n<b>Пользователи</b> могут подписаться на использование бота на определенный период времени: на <b>7, 30 или 60 дней.</b>'
                                    '\n\n<b>Подписка</b> дает полный доступ к функциям бота, увеличивая лимит получения ответов на любые вопросы, до <b>200</b> вопросов в сутки.',
                               parse_mode='html', reply_markup=kb.subs)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Вы не зарегистрированы ❌", parse_mode='html')


@dp.message_handler(text='Подписки ⭐️')
async def subs(message: Message):
    if (func.is_registered(message.chat.id)):
        await bot.send_message(chat_id=message.chat.id,
                               text='⭐️ <b>Cтандартная подписка</b> ⭐️'
                                    '\n\n📃 <b>Описание:</b>'
                                    '\nПозволяет пользоваться ботом ChatGpt.'
                                    '\nКоторый помогает пользователям получать ответы на различные вопросы в режиме реального времени, используя искусственный интеллект.'
                                    '\n ChatGPT может использоваться в образовательных, медицинских, финансовых и других отраслях.'
                                    '\n\n<b>➕ Преимущества подписки:</b>'
                                    '\n<b> — До 200 вопросов в сутки</b>'
                                    '\n<b> — Отключение рекламы</b>'
                                    '\n<b> — Снижение задержки между запросами до 15 секунд</b>',
                               parse_mode='html', reply_markup=kb.catalog_list)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Вы не зарегистрированы ❌", parse_mode='html')


@dp.message_handler(text='Моя подписка 🛠️')
async def check_have_time(message: Message):
    if (func.is_registered(message.chat.id)):
        have_time_sub = func.check_sub_status(message.chat.id) // 3600
        if have_time_sub > 0:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f"До конца подписки осталось <b>{have_time_sub}</b> часов ⌛️",
                                   parse_mode='html')
        else:
            await bot.send_message(chat_id=message.chat.id,
                                   text=f"Подписка <b>отсутствует</b> ❌", parse_mode='html')
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=f"Вы не зарегистрированы ❌", parse_mode='html')


@dp.message_handler(text='glck')
async def adm_glck(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(text='<b>Glock на месте!</b>', reply_markup=kb.admin_panel, parse_mode='html')
    else:
        await message.answer(text='Я тебя не понимаю!')


@dp.message_handler(text='Главное меню')
async def admin_panel(message: Message):
    await message.answer(text='<b>Main menu !</b>', reply_markup=kb.main_admin, parse_mode='html')


class NewsLetter(StatesGroup):
    text_news = State()


class NewKeys(StatesGroup):
    key_value = State()
    key_time = State()


class NewDocs(StatesGroup):
    QnumbSchet = State()
    Qdate = State()
    QbuyerData = State()
    QnumbContract = State()
    Qroute = State()
    QrouteDate = State()
    Qprice = State()



        # conn = sqlite3.connect('db.db')
        # cursor = conn.cursor()
        # cursor.execute("SELECT key, time, user, status FROM keys")
        # users = cursor.fetchall()


@dp.message_handler(text='Создать акт-счет')
async def make_docs(message: Message):
    await message.answer(text='<b>Введите номер счет-акта</b>', reply_markup=kb.admin_panel, parse_mode='html')
    await NewDocs.QnumbSchet.set()


@dp.message_handler(state=NewDocs.QnumbSchet)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['numbSchet'] = message.text
    await message.answer(text='<b>Введите дату поездки\nПример: 20 мая 2023</b>', parse_mode='html')
    await NewDocs.Qdate.set()


@dp.message_handler(state=NewDocs.Qdate)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
    await message.answer(text='<b>Введите данные заказчика</b>', parse_mode='html')
    await NewDocs.QbuyerData.set()


@dp.message_handler(state=NewDocs.QbuyerData)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['buyerData'] = message.text
    await message.answer(text='<b>Введите номер договора</b>', parse_mode='html')
    await NewDocs.QnumbContract.set()


@dp.message_handler(state=NewDocs.QnumbContract)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['numbContract'] = message.text
    await message.answer(text='<b>Введите маршрут поездки:</b>', parse_mode='html')
    await NewDocs.Qroute.set()


@dp.message_handler(state=NewDocs.Qroute)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['route'] = message.text
    await message.answer(text='<b>Введите дату состовления договра:\nПример: 20 мая 2023</b>', parse_mode='html')
    await NewDocs.QrouteDate.set()


@dp.message_handler(state=NewDocs.QrouteDate)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['routeDate'] = message.text
    await message.answer(text='<b>Введите сумму договра:</b>', parse_mode='html')
    await NewDocs.Qprice.set()


@dp.message_handler(state=NewDocs.Qprice)
async def make_docs(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
    schet_adr, akt_adr = func.create_docs(data['numbSchet'], data['date'], data['buyerData'], data['numbContract'],
                                          data['route'], data['routeDate'], data['price'])
    await state.finish()
    await message.answer(text='<b>Готово ✅</b>', parse_mode='html')
    with open(schet_adr, 'rb') as excel_file:
        await message.reply_document(excel_file)
    with open(akt_adr, 'rb') as excel_file:
        await message.reply_document(excel_file)


@dp.message_handler(text='Сделать рассылку')
async def newsletter(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(text='<b>Введите текст:</b>', parse_mode='html')
        await NewsLetter.text_news.set()
    else:
        await message.answer(text='Я тебя не понимаю!')




class AwaitMessages(StatesGroup):
    fio_add = State()
    phone_add = State()
    bank_name = State()
    bik = State()
    r_akk = State()
    k_akk = State()


@dp.message_handler(state=AwaitMessages.fio_add)
async def process_fio_add(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text
        match = re.search(r"\b\w{3,12}\b", data['fio'])
        if match:
            await message.answer('Введите ваш номер телефона 📞')
            await AwaitMessages.phone_add.set()
        else:
            await AwaitMessages.fio_add.set()
            await message.answer('Имя должно содержать от 3 до 12 символов 🚫')


@dp.message_handler(state=AwaitMessages.phone_add)
async def process_fio_add(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        phone_numbers = re.findall(r'\d{10,13}', data['phone'])
        if phone_numbers:
            connect = sqlite3.connect('db.db')
            cursor = connect.cursor()
            cursor.execute("UPDATE info SET user_phone=?, user_name=? WHERE user_id=?",
                           [data["phone"], data["fio"], message.chat.id])
            cursor.close()
            connect.commit()
            connect.close()
            await state.finish()
            await message.answer(f'Вы успешно зарегистрированы ✅')
        else:
            await AwaitMessages.phone_add.set()
            await message.answer(f'Введите коректный номер телефона ⛔️'
                                 f'\nНомер должен содержать только 10-13 цифр!')


@dp.message_handler(Command('check'))
async def check(message):
    if message.from_user.id == ADMIN_ID:
        keyboard = func.make_pay_inline_key[0](
            'https://yoomoney.ru/checkout/payments/v2/contract/bankcard?orderId=2bf84144-000f-5000-a000-1722b6f481dd')
        await message.answer(text='<b>Welcome BOSS!</b>', reply_markup=keyboard, parse_mode='html')


