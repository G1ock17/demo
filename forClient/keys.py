from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

main = ReplyKeyboardMarkup(resize_keyboard=True)
main.row('О нас  📖', 'Подписки ⭐️', 'Создать акт-счет')
main.row('Ввести ключ 🔑', 'Моя подписка 🛠️', 'Редактировать мои данные')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.row('О нас  📖', 'Подписки ⭐️', 'Создать акт-счет')
main_admin.row('Ввести ключ 🔑', 'Моя подписка 🛠️', 'Редактировать мои данные')
main_admin.add('glck')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.row('Ключи 🔑', 'Сгенерировать ключи', 'Сделать рассылку')
admin_panel.row('Список пользователей', 'Информация о продажах')
admin_panel.add('Главное меню')

CheckDeleteSubStatus = InlineKeyboardMarkup()
CheckDeleteSubStatus.add(InlineKeyboardButton(text='Проверить', callback_data='CheckPayStatus')).add(
    InlineKeyboardButton(text='Отменить', callback_data='DeletePaymentRequest'))


catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='7 дней', callback_data='light'),
                 InlineKeyboardButton(text='30 дней', callback_data='middle'),
                 InlineKeyboardButton(text='60 дней', callback_data='hard'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')
