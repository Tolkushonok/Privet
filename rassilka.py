from aiogram.fsm.state import State, StatesGroup

class MailingStates(StatesGroup):
    text = State()
    photo = State()
    confirm = State()
    confirm_photo = State()