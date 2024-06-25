from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling, start_webhook
from aiogram.utils import executor
from adminPanel import adminPanel
from simRent.app.db import Storage
from time import sleep
import datetime
import asyncio  # Добавлено для работы с асинхронностью

# from background import keep_alive
from data import config

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

db = Storage()

async def scheduled():
    """Функция для проверки сообщений"""
    while True:
        msg = db.get_messages()
        try:
            for rec in msg:
                await bot.send_message(rec['user_id'], f"{rec['phone']}:\n {rec['message']}")
                await asyncio.sleep(0.1)  # Используйте asyncio.sleep вместо time.sleep
                # дублируем в спецканал
                if config.GROUP_ID:
                    await bot.send_message(config.GROUP_ID, f"@{rec['user_name']} ({rec['user_id']}), ({rec['phone']}): {rec['message']}", disable_notification=True)
                    await asyncio.sleep(0.1)  # Используйте asyncio.sleep вместо time.sleep
                # удаляем если нет АПИ, иначе помечаем прочитанным
                if rec['id']:
                    db.set_read_msg(rec['id'])
                    print('Читаем смс №', rec['id'])
                else:
                    time = datetime.datetime.now()
                    time.strftime('%H-%M')
                    print('Отправляем смс №', rec['id'], time)
                    db.set_read_msg(rec['id'])
                    #   db.del_msg(rec['id'])
        except Exception as e:
            print(f"Ошибка при обработке сообщений: {e}")
        await asyncio.sleep(1)  # Интервал между проверками, можно настроить по необходимости

if __name__ == '__main__':
    from registration import dp
    from myProfile import dp
    from instructions import dp
    from outMoney import dp
    from support import dp
    from adminPanel import dp

    # Запуск планировщика задач
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled())

    executor.start_polling(dp, skip_updates=True)
