from aiogram.dispatcher.filters.state import StatesGroup, State

class Registration(StatesGroup):
    wait_first_name = State()
    wait_last_name = State()
    wait_role = State()
    wait_secret_code = State()
    wait_email = State()
    wait_password = State()
    wait_confirm_password = State()
    wait_confirm_registration = State()