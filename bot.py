import logging
import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.filters.command import Command
from db import Database
from Bot_rassilka import register_mailing_handlers  # Импорт из Bot_rassilka

logging.basicConfig(level=logging.INFO)
API_KEY = "8446422036:AAFQTFxdA7Vu2ckjYJRTFVCnNvEuyCoe0MI"
bot = Bot(API_KEY)
dp = Dispatcher()
db = Database()

@dp.message(Command("/start"))
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        if not await db.user_exists(message.from_user.id):
            await db.add_user(message.from_user.id)
            await message.answer("Привет!")
        else:
            await message.answer("С возвращением!")


async def main():
    await db.create_tables()
    register_mailing_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())