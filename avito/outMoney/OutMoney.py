from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentTypes, InlineKeyboardMarkup, ReplyKeyboardMarkup, \
    KeyboardButton
from main import dp, bot
from database import functions
from keyboards import keys


class OutMoney(StatesGroup):
    Request = State()
    # Value = State()


@dp.message_handler(text='Вывести средства')
async def out_money_request(message: Message):

    data = functions.get_user_information(message.from_user.id)
    if data[2] == 0:
        await message.answer(text=f'Вам недоступен вывод средств'
                                  f'\nВаш баланс равен 0p')
    else:
        await OutMoney.Request.set()
        await message.answer(text=f'Ваш баланс: {data[2]}p'
                              f'\nВведите сумму которую вы хотите вывести:', reply_markup=keys.cancel())


@dp.message_handler(state=OutMoney.Request, content_types=ContentTypes.TEXT)
async def out_money_value(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['value'] = message.text
    user_info = functions.get_user_information(message.from_user.id)
    if message.text.isdigit() and int(message.text) <= user_info[2]:
        enter_value = message.text
        await message.answer(text=f'Ваши реквезиты: {user_info[3]}'
                                  f'\nСумма вывода: {enter_value}p'
                                  f'\nУбедитесь что реквезиты верны, после подтвердите транзакцию.', parse_mode='html',
                             reply_markup=keys.confirmation_keyboard_for_out_money())
    else:
        await message.answer(text='Введите корректную сумму для вывода')


@dp.callback_query_handler(lambda callback: callback.data.startswith('outmoney_'), state=OutMoney.Request)
async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        pass
    action, status = callback.data.split('_')
    user_info = functions.get_user_information(callback.from_user.id)
    enter_value = data['value']
    if status == "confirm":
        functions.update_user_balance(callback.from_user.id, int(enter_value), '-')
        reqID = functions.create_withdrawal_request(callback.from_user.id, user_info[3], enter_value)
        await callback.message.answer(text=f'Заявка <b>#{reqID}</b> успешно созданна! '
                                           f'\nСумма {enter_value}р'
                                           f'\nРеквезиты {user_info[3]}', parse_mode='html', reply_markup=keys.main_markup())
        await state.finish()

    elif status == "rewrite":
        await OutMoney.Request.set()
        await callback.message.answer(text="Введите вашу новую сумму.")
