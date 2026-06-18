import logging
import asyncio
from aiogram import Bot, types, Dispatcher
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from db import Database, User, async_session_maker
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
API_KEY = "8446422036:AAGLdFcjYLoZduqDV_yoAG2XS1Lgez_WtDs"
bot = Bot(API_KEY)
dp = Dispatcher()
db = Database()

ADMIN_ID = 6047277216


# Класс состояний для рассылки
class MailingStates(StatesGroup):
    text = State()
    photo = State()
    confirm = State()
    confirm_photo = State()


# Функция для получения всех пользователей
async def get_all_users():
    async with async_session_maker() as session:
        result = await session.execute(select(User.user_id))
        return [row[0] for row in result.all()]


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        if not await db.user_exists(message.from_user.id):
            await db.add_user(message.from_user.id)
            await message.answer("Привет! ")
        else:
            await message.answer("С возвращением!")


# Обработчик команды /mailing
@dp.message(Command("mailing"))
async def start_mailing(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет прав на рассылку")
        return
    await message.answer("Введите текст рассылки:")
    await state.set_state(MailingStates.text)


# Получение текста рассылки
@dp.message(MailingStates.text)
async def get_mailing_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить фото", callback_data="add_photo"),
            InlineKeyboardButton(text="Далее", callback_data="next"),
            InlineKeyboardButton(text="Отменить", callback_data="quit")
        ]
    ])
    await message.answer(
        text=f"Текст рассылки:\n\n{message.text}",
        reply_markup=markup
    )
    await state.set_state(MailingStates.confirm)


# Добавление фото
@dp.callback_query(F.data == "add_photo")
async def add_photo(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Пришлите фото:")
    await state.set_state(MailingStates.photo)
    await call.answer()


# Получение фото
@dp.message(MailingStates.photo, F.content_type == ContentType.PHOTO)
async def get_photo(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo=photo_file_id)
    data = await state.get_data()
    text = data.get("text", "")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Далее", callback_data="next"),
            InlineKeyboardButton(text="Отменить", callback_data="quit")
        ]
    ])
    await message.answer_photo(
        photo=photo_file_id,
        caption=text,
        reply_markup=markup
    )
    await state.set_state(MailingStates.confirm_photo)


# Если прислали не фото
@dp.message(MailingStates.photo)
async def no_photo(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить", callback_data="quit")]
    ])
    await message.answer("Пришлите фотографию", reply_markup=markup)


# Отправка рассылки
@dp.callback_query(F.data == "next")
async def send_mailing(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "Текст не указан")
    photo = data.get("photo")
    users = await get_all_users()

    if not users:
        await call.message.answer("Нет пользователей для рассылки")
        await state.finish()
        await call.answer()
        return

    count = 0
    for user_id in users:
        try:
            if photo:
                await call.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=text
                )
            else:
                await call.bot.send_message(
                    chat_id=user_id,
                    text=text
                )
            count += 1
            await asyncio.sleep(0.05)  # Задержка, чтобы не превысить лимиты Telegram
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")
            pass

    await call.message.answer(f"Рассылка выполнена! Отправлено: {count}")
    await state.finish()
    await call.answer()


# Отмена рассылки
@dp.callback_query(F.data == "quit")
async def quit_mailing(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("Рассылка отменена")
    await call.answer()


async def main():
    # Создаём таблицу при запуске
    await db.create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())