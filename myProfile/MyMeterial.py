from aiogram.types import Message
from main import dp, bot
from database import functions
from aiogram.types import Message, CallbackQuery, ContentTypes, InlineKeyboardMarkup, InlineKeyboardButton


def ikb_user_materials(user_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    names = functions.get_user_materials(user_id)
    if names:
        materials = [name[0] for name in names]
        for material in materials:
            button = InlineKeyboardButton(material, callback_data=f"vin_{material}")
            keyboard.add(button)
        return keyboard
    else:
        return None


@dp.message_handler(text='Мой материал')
async def my_profile(message: Message):
    keyboard = ikb_user_materials(message.from_user.id)
    if keyboard:
        await message.answer(text=f'Ваш материал:', parse_mode='html', reply_markup=keyboard)
    else:
        await message.answer(text=f'У вас нет материала')


@dp.callback_query_handler(lambda c: c.data.startswith('vin_'))
async def get_material(callback_query: CallbackQuery):
    vin_id = callback_query.data.split('_')[1]

    try:
        description = functions.get_material(vin_id)

        for request in description:
            request_id = request[0]
            car_name = request[1]
            vin = request[2]
            gos_numb = request[3]
            complectation = request[4]
            color = request[5]
            mileage = request[6]
            car_state = request[7]
            pts_state = request[8]
            owner_value = request[9]
            description = request[10]
            place = request[11]
            price = request[12]


            await callback_query.message.answer(
                text=f'Материал №{request_id}\n\n'
                     f'Название машины: <code>{car_name}</code>\n'
                     f'Vin номер: <code>{vin}</code>\n'
                     f'Гос номер: <code>{gos_numb}</code>\n'
                     f'Комплектация: <code>{complectation}</code>\n'
                     f'Цвет: <code>{color}</code>\n'
                     f'Пробег: <code>{mileage}</code>\n'
                     f'Состояние машины: <code>{car_state}</code>\n'
                     f'ПТС: <code>{pts_state}</code>\n'
                     f'Владельцев по ПТС: <code>{owner_value}</code>\n'
                     f'Описание автомобиля: <code>{description}</code>\n'
                     f'Место осмотра: <code>{place}</code>\n'
                     f'Цена: <code>{price}</code>\n\n'

                     f'Вид объявления: Продаю личный автомобиль.\n\n'
                     
                     f'Используйте номер телефона который вам выдали\n'
                     f'',
                parse_mode='html'
            )
    except Exception as e:
        print(f"Произошла ошибка при обработке заявки: {e}")
