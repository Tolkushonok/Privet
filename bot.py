import logging
import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.filters.command import Command
from db import Database


logging.basicConfig(level=logging.INFO)
API_KEY = "8446422036:AAFCFKNquXn_CVIfW1jL0kZWLpCo5HK7GfY"
bot = Bot(API_KEY)
dp = Dispatcher()
db = Database('databasse.db')

@dp.message(Command("start"))

async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        if not db.user_exists(message.from_user.id):
            db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Привет!")



async def main():
    await dp.start_polling(bot)


if __name__ =="__main__":
    asyncio.run(main())
