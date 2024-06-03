from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ContentTypes, InlineKeyboardMarkup

from database import functions
from keyboards import keys
from main import dp, bot


class Registration(StatesGroup):
    WaitingForPhoneNumber = State()


@dp.message_handler(Command('start'), state='*')
async def start(message: Message, state: FSMContext):
    await state.finish()
    if functions.add_user(user_id=message.from_user.id, user_name=message.from_user.username):
        await bot.send_message(chat_id=message.chat.id,
                               text='Привет!'
                                    '\nМы крупный автосалон которому нужно много объявлений на авито'
                                    '\nМы предлагаем высокую ставку и долгосрочные отношения.'
                                    '\nЧтобы начать работу нажмите на кнопку <b>Инструкция</b>.',
                               reply_markup=None, parse_mode='html')
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Вы в главном меню.', reply_markup=keys.main_markup())


# @dp.callback_query_handler(lambda c: c.data == 'registration')
# async def support_request(callback: CallbackQuery):
#     await callback.message.answer(text='Пожалуйста нажмите на кнопку <b>"Поделиться номером"</b>',
#                                   reply_markup=keys.share_phone_markup(),
#                                   parse_mode='html')
#     await Registration.WaitingForPhoneNumber.set()
#     await callback.answer()
#
#
# @dp.message_handler(content_types=ContentTypes.CONTACT, state=Registration.WaitingForPhoneNumber)
# async def handle_contact1(message: Message):
#     phone_number = message.contact.phone_number
#     await message.answer(f"Вы поделились номером: {phone_number}\n\n"
#                          "Пожалуйста, подтвердите, что номер верный:",
#                          reply_markup=keys.get_confirmation_keyboard(phone_number))
#
#
# @dp.callback_query_handler(lambda callback: callback.data.startswith(('confirm_', 'rewrite_')),
#                            state=Registration.WaitingForPhoneNumber)
# async def handle_confirmation(callback: CallbackQuery, state: FSMContext):
#     action, phone_number = callback.data.split('_')
#     if action == "confirm":
#         functions.add_phone(callback.from_user.id, phone_number)
#         await callback.message.answer(text="Благодарим за регестрацию, вы можете приступать к работе",
#                                       reply_markup=keys.main_markup())
#         await state.finish()
#
#     elif action == "rewrite":
#         await Registration.WaitingForPhoneNumber.set()
#         await callback.message.answer(text="Пожалуйста, введите свой номер телефона еще раз.")


@dp.message_handler(text='Отмена', state='*')
async def my_profile(message: Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text=f'Действие отменено', reply_markup=keys.main_markup())
    await state.finish()
