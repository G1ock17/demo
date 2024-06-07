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
    markup.row('Взять материал', 'Мой материал', 'Проверить объявление')
    markup.row('Вывести средства', 'Написать в поддержку', 'Изменить реквезиты')
    return markup


def admin_menu():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Заявки на материал", callback_data=f"req_material"),
                 InlineKeyboardButton("Проверка объявлений", callback_data=f"req_anc"),
                 InlineKeyboardButton("Заявки на выплату", callback_data=f"req_payment"))
    return keyboard


def confirmation_keyboard_for_out_money():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Подтвердить 👍", callback_data=f"outmoney_confirm"),
                 InlineKeyboardButton("Перепишу ❌", callback_data=f"outmoney_rewrite"))
    return keyboard


def ikb(text, callback):
    button = InlineKeyboardButton(text=text, callback_data=callback)
    return button
