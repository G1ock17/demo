from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

back_message = '👈 Назад'
confirm_message = '✅ Подтвердить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'


def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)
    return markup


def share_phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Поделиться номером', request_contact=True))
    return markup

def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)
    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)
    return markup


def defolt_marup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row('Написать продавцу')


def get_phone_request_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Поделиться номером", request_contact=True))
    return keyboard


def get_confirmation_keyboard(phone_number):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Все верно 👍", callback_data=f"confirm_{phone_number}"),
                 InlineKeyboardButton("Перепишу ❌", callback_data=f"rewrite_{phone_number}"))
    return keyboard


def get_feedback_confirmation_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Бонус отправлен ✅", callback_data='bonus_sent'),
        InlineKeyboardButton("Отклонить ❌", callback_data='reject')
    )
    return keyboard

def ikb(text, callback):
    button = InlineKeyboardButton(text=text, callback_data=callback)
    return button
