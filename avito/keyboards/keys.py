from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def cancel():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Отмена'))
    return markup


def share_phone_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Поделиться номером', request_contact=True))
    return markup


def main_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row('Мой профиль', 'Мои заявки', 'Инструкция')
    markup.row('Взять материал', 'Проверить объявление')
    markup.row('Вывести средства', 'Написать в поддержку', 'Изменить реквезиты')
    return markup


def get_phone_request_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Поделиться номером", request_contact=True))
    return keyboard


def get_confirmation_keyboard(phone_number):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Все верно 👍", callback_data=f"confirm_{phone_number}"),
                 InlineKeyboardButton("Перепишу ❌", callback_data=f"rewrite_{phone_number}"))
    return keyboard


def confirmation_keyboard_for_out_money():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Подтвердить 👍", callback_data=f"outmoney_confirm"),
                 InlineKeyboardButton("Перепишу ❌", callback_data=f"outmoney_rewrite"))
    return keyboard


def ikb(text, callback):
    button = InlineKeyboardButton(text=text, callback_data=callback)
    return button
