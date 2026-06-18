from aiogram import Bot, types, Dispatcher
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram import F
from rassilka import MailingStates
import asyncio

# Укажи свой Telegram ID здесь
ADMIN_ID = 6047277216  # ЗАМЕНИ НА СВОЙ ID!


async def get_all_users():
    from sqlalchemy import select
    from db import User, async_session_maker
    async with async_session_maker() as session:
        result = await session.execute(select(User.user_id))
        return [row[0] for row in result.all()]


def register_mailing_handlers(dp: Dispatcher):
    @dp.message(Command("/mailing"))
    async def start_mailing(message: types.Message, state: FSMContext):
        if message.from_user.id != ADMIN_ID:
            await message.answer("yет прав на рассылку")
            return
        await message.answer('dведите текст ')
        await state.set_state(MailingStates.text)

    @dp.message(MailingStates.text)
    async def get_mailing_text(message: types.Message, state: FSMContext):
        answer = message.text
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Добавить фотографию", callback_data="add_photo"),
                InlineKeyboardButton(text="Далее", callback_data="next"),
                InlineKeyboardButton(text="Отменить", callback_data="quit")
            ]
        ])
        await state.update_data(text=answer)
        await message.answer(text=answer, reply_markup=markup)
        await state.set_state(MailingStates.confirm)

    @dp.callback_query(F.data == "add_photo")
    async def add_photo(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer("Пришлите фото")
        await state.set_state(MailingStates.photo)
        await call.answer()

    @dp.message(MailingStates.photo, F.content_type == ContentType.PHOTO)
    async def get_photo(message: types.Message, state: FSMContext):
        photo_file_id = message.photo[-1].file_id
        await state.update_data(photo=photo_file_id)
        data = await state.get_data()
        text = data.get("text")

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Далее", callback_data="next"),
                InlineKeyboardButton(text="Отменить", callback_data="quit")
            ]
        ])
        await message.answer_photo(photo=photo_file_id, caption=text, reply_markup=markup)
        await state.set_state(MailingStates.confirm_photo)

    @dp.message(MailingStates.photo)
    async def no_photo(message: types.Message):
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="quit")]
        ])
        await message.answer('Пришлите фотографию', reply_markup=markup)

    @dp.callback_query(F.data == "next")
    async def send_mailing(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        text = data.get("text")
        photo = data.get("photo")

        users = await get_all_users()
        count = 0


        for user_id in users:
            try:
                if photo:
                    await call.bot.send_photo(chat_id=user_id, photo=photo, caption=text)
                else:
                    await call.bot.send_message(chat_id=user_id, text=text)
                count += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass

        await call.message.answer(f'Рассылка выполнена {count} ')
        await state.finish()
        await call.answer()

    @dp.callback_query(F.data == "quit")
    async def quit_mailing(call: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await call.message.answer('Рассылка отменена')
        await call.answer()