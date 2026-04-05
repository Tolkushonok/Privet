import logging
from aiogram import Bot, Dispatcher,executor , types
from db import Database
import sqlite3

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8446422036:AAFCFKNquXn_CVIfW1jL0kZWLpCo5HK7GfY")
dp = Dispatcher(bot)
db = Database('databasse.db')

@dp.message_handler(commands=["/start"])
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Привет!")



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

