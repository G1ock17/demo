from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# from background import keep_alive

from data import config

storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

# keep_alive()
if __name__ == '__main__':
    from registration import dp
    from myProfile import dp
    from instructions import dp
    from outMoney import dp
    from support import dp

    executor.start_polling(dp, skip_updates=True)
